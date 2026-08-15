"""publishers/meta.py — publicação oficial no Instagram (Graph API, v23.0).

Rota (Instagram Login, host graph.instagram.com):
1. GET /{<IG_USER_ID>}/content_publishing_limit — quota estourada => aborta
2. Valida cada URL dos slides: curl -I => 200 + image/jpeg, sem redirect
3. Por slide, na ordem: POST /{<IG_USER_ID>}/media (image_url, is_carousel_item=true, alt_text)
4. POST /{<IG_USER_ID>}/media (media_type=CAROUSEL, children=<ids na ordem>, caption)
   Body form-encoded — NUNCA query string (hashtag quebra)
5. Poll ?fields=status_code até FINISHED — backoff 3s→6s→12s, máx 8
6. POST /media_publish (creation_id)
7. GET /{media_id}?fields=permalink — sem permalink = falha, mesmo com 200 no publish

Retry SÓ em erro temporário (5xx, timeout, rate limit/429/code 4) com backoff.
Máx 2 tentativas. Token/permissão/formato/política => reporta, não repete.
Container expira em 24h: cada tentativa recria containers do zero (nunca reusa ID).
Token jamais em log (redige se a API ecoar).
"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

HOST = "https://graph.instagram.com/v23.0"
POLL_BACKOFF = [3, 6, 12]
POLL_MAX = 8
MAX_ATTEMPTS = 2


def _redact(s: str, token: str) -> str:
    return s.replace(token, "<redacted>") if token and token in s else s


def _err_text(parsed: dict, fallback: str) -> str:
    err = parsed.get("error") if isinstance(parsed, dict) else None
    if isinstance(err, dict):
        parts = []
        if err.get("code"):
            parts.append(f"code={err['code']}")
        if err.get("error_subcode"):
            parts.append(f"subcode={err['error_subcode']}")
        parts.append(str(err.get("message", "")))
        text = " — ".join(p for p in parts if p)
        return text or fallback
    return fallback


def _is_retryable(status: int | None, parsed: dict) -> bool:
    """Só erro temporário: 5xx, 429, timeout, rate limit (code 4)."""
    if status is None:
        return True  # timeout/transport
    if status >= 500 or status == 429:
        return True
    err = parsed.get("error") if isinstance(parsed, dict) else None
    if isinstance(err, dict) and err.get("code") == 4:
        return True  # application request limit
    return False


def _request(method: str, url: str, token: str, data: dict | None = None) -> tuple[int | None, dict]:
    body = None
    headers = {}
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        return e.code, parsed
    except Exception:
        return None, {}


def _check_url(url: str) -> tuple[bool, str]:
    """curl -I: 200 + image/jpeg + sem redirect. Nunca loga o URL com token."""
    r = subprocess.run(["curl", "-sI", "--max-time", "20", url], capture_output=True, text=True)
    if r.returncode != 0:
        return False, f"curl falhou em {url}"
    lines = [ln.strip().lower() for ln in r.stdout.splitlines() if ln.strip()]
    if not lines:
        return False, f"resposta vazia de {url}"
    status_line = lines[0]
    if " 200 " not in f" {status_line} " and not status_line.startswith("http/2 200"):
        return False, f"{url} -> {status_line}"
    ctype = next((ln for ln in lines if ln.startswith("content-type:")), "")
    if "image/jpeg" not in ctype:
        return False, f"{url} content-type inesperado: {ctype or 'ausente'}"
    if any(ln.startswith("location:") for ln in lines):
        return False, f"{url} respondeu redirect"
    return True, "ok"


def _attempt(user_id: str, token: str, urls: list[str], alt_texts: list[str], caption: str) -> tuple[bool, bool, str | None, str]:
    """Uma tentativa completa. Retorna (retryable, ok, url, erro)."""
    # 1. quota
    qs = urllib.parse.urlencode({"access_token": token})
    status, parsed = _request("GET", f"{HOST}/{user_id}/content_publishing_limit?{qs}", token)
    if status != 200:
        err = f"content_publishing_limit: HTTP {status} {_err_text(parsed, 'sem corpo')}"
        return (_is_retryable(status, parsed), False, None, err)
    try:
        item = (parsed.get("data") or [{}])[0]
        used = int(item.get("quota_usage") or 0)
        total = int(item.get("config", {}).get("quota_total") or 0)
        if total and used >= total:
            return (False, False, None, f"quota estourada: {used}/{total} hoje")
    except (TypeError, ValueError, KeyError, IndexError):
        pass  # resposta sem quota — o publish dirá se houver limite

    # 2. URLs dos slides
    for u in urls:
        ok, why = _check_url(u)
        if not ok:
            return (False, False, None, why)

    # 3. containers por slide (ordem importa)
    children: list[str] = []
    for i, u in enumerate(urls, 1):
        alt = alt_texts[i - 1] if i - 1 < len(alt_texts) else ""
        status, parsed = _request(
            "POST",
            f"{HOST}/{user_id}/media",
            token,
            {"image_url": u, "is_carousel_item": "true", "alt_text": alt, "access_token": token},
        )
        if status != 200 or "id" not in parsed:
            err = f"media slide {i}: HTTP {status} {_err_text(parsed, 'sem id')}"
            return (_is_retryable(status, parsed), False, None, err)
        children.append(str(parsed["id"]))

    # 4. container carrossel — form-encoded, nunca query string
    status, parsed = _request(
        "POST",
        f"{HOST}/{user_id}/media",
        token,
        {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption, "access_token": token},
    )
    if status != 200 or "id" not in parsed:
        err = f"carousel container: HTTP {status} {_err_text(parsed, 'sem id')}"
        return (_is_retryable(status, parsed), False, None, err)
    creation_id = str(parsed["id"])

    # 5. poll status_code
    for i in range(POLL_MAX):
        qs = urllib.parse.urlencode({"fields": "status_code", "access_token": token})
        status, parsed = _request("GET", f"{HOST}/{creation_id}?{qs}", token)
        if status != 200:
            err = f"poll: HTTP {status} {_err_text(parsed, 'sem corpo')}"
            return (_is_retryable(status, parsed), False, None, err)
        sc = parsed.get("status_code")
        if sc == "FINISHED":
            break
        if sc in ("ERROR", "EXPIRED"):
            return (False, False, None, f"container {creation_id} status_code={sc}")
        if i < POLL_MAX - 1:
            time.sleep(POLL_BACKOFF[min(i, len(POLL_BACKOFF) - 1)])
    else:
        return (False, False, None, f"poll esgotado ({POLL_MAX}x) sem FINISHED")

    # 6. publish
    status, parsed = _request(
        "POST",
        f"{HOST}/{user_id}/media_publish",
        token,
        {"creation_id": creation_id, "access_token": token},
    )
    if status != 200 or "id" not in parsed:
        err = f"media_publish: HTTP {status} {_err_text(parsed, 'sem id')}"
        return (_is_retryable(status, parsed), False, None, err)
    media_id = str(parsed["id"])

    # 7. permalink — sem permalink = falha, mesmo com 200 no publish
    qs = urllib.parse.urlencode({"fields": "permalink", "access_token": token})
    status, parsed = _request("GET", f"{HOST}/{media_id}?{qs}", token)
    permalink = parsed.get("permalink") if isinstance(parsed, dict) else None
    if status != 200 or not permalink:
        err = f"permalink: HTTP {status} {_err_text(parsed, 'sem permalink')}"
        return (False, False, None, err)

    return (False, True, permalink, "")


def _attempt_single(user_id: str, token: str, url: str, alt_text: str, caption: str) -> tuple[bool, bool, str | None, str]:
    """Uma tentativa completa de imagem única. Retorna (retryable, ok, url, erro)."""
    # 1. quota
    qs = urllib.parse.urlencode({"access_token": token})
    status, parsed = _request("GET", f"{HOST}/{user_id}/content_publishing_limit?{qs}", token)
    if status != 200:
        err = f"content_publishing_limit: HTTP {status} {_err_text(parsed, 'sem corpo')}"
        return (_is_retryable(status, parsed), False, None, err)
    try:
        item = (parsed.get("data") or [{}])[0]
        used = int(item.get("quota_usage") or 0)
        total = int(item.get("config", {}).get("quota_total") or 0)
        if total and used >= total:
            return (False, False, None, f"quota estourada: {used}/{total} hoje")
    except (TypeError, ValueError, KeyError, IndexError):
        pass

    # 2. URL da imagem
    ok, why = _check_url(url)
    if not ok:
        return (False, False, None, why)

    # 3. container único (media_type=IMAGE)
    data = {"image_url": url, "caption": caption, "access_token": token}
    if alt_text:
        data["alt_text"] = alt_text
    status, parsed = _request("POST", f"{HOST}/{user_id}/media", token, data)
    if status != 200 or "id" not in parsed:
        err = f"media imagem: HTTP {status} {_err_text(parsed, 'sem id')}"
        return (_is_retryable(status, parsed), False, None, err)
    creation_id = str(parsed["id"])

    # 4. poll status_code
    for i in range(POLL_MAX):
        qs = urllib.parse.urlencode({"fields": "status_code", "access_token": token})
        status, parsed = _request("GET", f"{HOST}/{creation_id}?{qs}", token)
        if status != 200:
            err = f"poll: HTTP {status} {_err_text(parsed, 'sem corpo')}"
            return (_is_retryable(status, parsed), False, None, err)
        sc = parsed.get("status_code")
        if sc == "FINISHED":
            break
        if sc in ("ERROR", "EXPIRED"):
            return (False, False, None, f"container {creation_id} status_code={sc}")
        if i < POLL_MAX - 1:
            time.sleep(POLL_BACKOFF[min(i, len(POLL_BACKOFF) - 1)])
    else:
        return (False, False, None, f"poll esgotado ({POLL_MAX}x) sem FINISHED")

    # 5. publish
    status, parsed = _request(
        "POST",
        f"{HOST}/{user_id}/media_publish",
        token,
        {"creation_id": creation_id, "access_token": token},
    )
    if status != 200 or "id" not in parsed:
        err = f"media_publish: HTTP {status} {_err_text(parsed, 'sem id')}"
        return (_is_retryable(status, parsed), False, None, err)
    media_id = str(parsed["id"])

    # 6. permalink — sem permalink = falha, mesmo com 200 no publish
    qs = urllib.parse.urlencode({"fields": "permalink", "access_token": token})
    status, parsed = _request("GET", f"{HOST}/{media_id}?{qs}", token)
    permalink = parsed.get("permalink") if isinstance(parsed, dict) else None
    if status != 200 or not permalink:
        err = f"permalink: HTTP {status} {_err_text(parsed, 'sem permalink')}"
        return (False, False, None, err)

    return (False, True, permalink, "")


def publish(package: dict, env: dict) -> dict:
    """Publica carrossel ou imagem única (campo formato). Retorna {"ok": bool, "url": str|None, "error": str|None}."""
    token = env.get("IG_ACCESS_TOKEN", "")
    user_id = env.get("IG_USER_ID", "")
    if not token or not user_id:
        return {"ok": False, "url": None, "error": "faltam IG_ACCESS_TOKEN/<IG_USER_ID> no .env"}
    urls = package.get("urls") or []
    alt_texts = package.get("alt_texts") or []
    caption = package.get("caption", "")
    formato = package.get("formato") or "carrossel"
    if not urls:
        return {"ok": False, "url": None, "error": "package sem urls — rode upload antes"}

    if formato == "infografico":
        if len(urls) != 1:
            return {"ok": False, "url": None, "error": f"infografico exige 1 url, recebeu {len(urls)}"}
        alt = alt_texts[0] if alt_texts else ""
        last = "erro desconhecido"
        for attempt in range(1, MAX_ATTEMPTS + 1):
            retryable, ok, url, err = _attempt_single(user_id, token, urls[0], alt, caption)
            if ok:
                return {"ok": True, "url": url, "error": None}
            last = err
            if not retryable or attempt == MAX_ATTEMPTS:
                break
            time.sleep(3 * attempt)
        return {"ok": False, "url": None, "error": last}

    # carrossel (padrão)
    last = "erro desconhecido"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        retryable, ok, url, err = _attempt(user_id, token, urls, alt_texts, caption)
        if ok:
            return {"ok": True, "url": url, "error": None}
        last = err
        if not retryable or attempt == MAX_ATTEMPTS:
            break
        time.sleep(3 * attempt)
    return {"ok": False, "url": None, "error": last}
