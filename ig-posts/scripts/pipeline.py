#!/usr/bin/env python3
"""pipeline.py — etapas determinísticas do ig-posts.

Subcomandos: render | upload | package | publish | status | validate

- Pesquisa e copy são feitas pelo AGENTE (LLM) e gravadas em <slug>/copy.json.
- Nenhuma lógica de rede fora de publishers/.
- Credenciais: ~/.hermes/.env (nunca impressas).
- Checkpoint: render re-renderiza só slides ausentes/inválidos.
"""
from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
ENV_FILE = HOME / ".hermes" / ".env"
SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "slide-template.html"
INFO_TEMPLATE = SKILL_DIR / "templates" / "infografico-template.html"
BASE_OUT = HOME / ".hermes" / "ig"
FONTS_DIR = HOME / ".fonts"


def resolve_render_tokens(t: str) -> str:
    """Troca tokens de caminho por file:// absolutos no momento do render.

    Os templates commitados usam {{FONTS_DIR}}/{{ASSETS_DIR}} (sem paths do
    servidor — gate pre-push); aqui resolvem para o filesystem real."""
    return (t.replace("{{FONTS_DIR}}", FONTS_DIR.as_uri())
             .replace("{{ASSETS_DIR}}", (SKILL_DIR / "assets").as_uri()))

W, H = 1080, 1350
JPEG_Q = 90


# ---------- util ----------

def log(msg: str) -> None:
    print(msg, flush=True)


def err(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def load_env() -> dict:
    """Lê ~/.hermes/.env. Nunca imprime valores de token."""
    if not ENV_FILE.exists():
        err(f"{ENV_FILE} não existe — Fase 0 (app Meta + token + R2) pendente")
    env: dict[str, str] = {}
    for raw in ENV_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    missing = [k for k in ("IG_ACCESS_TOKEN", "IG_USER_ID", "R2_ACCESS_KEY_ID",
                           "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT", "R2_BUCKET",
                           "R2_PUBLIC_URL") if not env.get(k)]
    if missing:
        err(f"~/.hermes/.env sem as chaves: {', '.join(missing)}")
    return env


def slug_dir(slug: str) -> Path:
    return BASE_OUT / slug


def load_json(path: Path) -> dict:
    if not path.exists():
        err(f"{path} não existe")
    return json.loads(path.read_text())


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_state(slug: str) -> dict:
    p = slug_dir(slug) / "state.json"
    return json.loads(p.read_text()) if p.exists() else {"slug": slug, "stage": "pesquisa"}


def save_state(slug: str, **updates) -> dict:
    st = load_state(slug)
    st.update(updates)
    st["slug"] = slug
    st["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save_json(slug_dir(slug) / "state.json", st)
    return st


def ensure_not_published(slug: str) -> None:
    st = load_state(slug)
    if st.get("stage") == "publicado":
        err(f"slug '{slug}' já publicado (permalink: {st.get('permalink')}) — recuso republicar")


def validate_jpeg(path: Path) -> tuple[bool, str]:
    """Exige exatamente 1080x1350 e JPEG. Retorna (ok, motivo)."""
    if not path.exists():
        return False, "arquivo não existe"
    try:
        from PIL import Image
        with Image.open(path) as im:
            fmt, size = im.format, im.size
    except Exception as e:  # noqa: BLE001
        return False, f"não é imagem válida: {e}"
    if fmt != "JPEG":
        return False, f"formato {fmt} — deve ser JPEG (API da Meta rejeita PNG)"
    if size != (W, H):
        return False, f"dimensões {size[0]}x{size[1]} — deve ser exatamente {W}x{H}"
    return True, "ok"


# ---------- subcomandos ----------

def _resample():
    from PIL import Image
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


def _pad_to(im, w: int, h: int, fill=(247, 235, 220)):
    """Letterbox em w×h. Só para fonte mais estreita que 4:5 (9:16)."""
    from PIL import Image
    sw, sh = im.size
    scale = min(w / sw, h / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    im = im.resize((nw, nh), _resample())
    canvas = Image.new("RGB", (w, h), fill)
    canvas.paste(im, ((w - nw) // 2, (h - nh) // 2))
    return canvas


def _cover_to(im, w: int, h: int):
    """Cover-crop central para w×h. Square→4:5 corta laterais, não topo/base."""
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im = im.resize((nw, nh), _resample())
    left = (nw - w) // 2
    top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def _fit_to(im, w: int, h: int):
    """Fonte ~4:5 (0.78–0.82) → resize proporcional, sem crop/pad.

    Fonte fora da faixa (9:16 antiga, square legado) → cover se larga,
    pad se estreita — compat com artefatos antigos, não é o caminho novo.
    """
    sw, sh = im.size
    ratio = sw / sh
    target = w / h  # 0.8
    if 0.78 <= ratio <= 0.82:
        # Stretch exato. 928×1152 (0.806) → 1080×1350 (0.800) = 0,7% — invisível.
        # NUNCA canvas+paste: isso recria a barra creme.
        return im.resize((w, h), _resample()), "resize"
    if ratio >= target:
        return _cover_to(im, w, h), "cover"
    return _pad_to(im, w, h), "pad"


def _render_infografico(slug: str, copy: dict, out: Path) -> None:
    """Renderiza 1 imagem 1080×1350: blocos via template HTML, ou 01.jpg já gerado (image_generate)."""
    dest = out / "01.jpg"
    ok, _ = validate_jpeg(dest)
    if ok:
        log("[checkpoint] 01.jpg já renderizado e válido — pulando")
    else:
        blocos = copy.get("blocos")
        if not blocos or not isinstance(blocos, list) or not 1 <= len(blocos) <= 8:
            err("infografico: copy.json precisa de 'blocos' (1-8) para render HTML, ou de 01.jpg já gerado (image_generate + convert)")
        tmpl = resolve_render_tokens(INFO_TEMPLATE.read_text()) if INFO_TEMPLATE.exists() else err(f"template não encontrado: {INFO_TEMPLATE}")
        parts = []
        for i, b in enumerate(blocos, 1):
            titulo = html.escape(str(b.get("titulo", "")))
            corpo = html.escape(str(b.get("corpo", "")))
            parts.append(
                f'<div class="block"><div class="num">{i:02d}</div>'
                f'<div class="body"><div class="btitulo">{titulo}</div>'
                f'<div class="bcorpo">{corpo}</div></div></div>'
            )
        doc = tmpl.replace("{{blocos}}", '<div class="rule"></div>'.join(parts))
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": W, "height": H})
            page.set_content(doc, wait_until="load")
            page.screenshot(path=str(dest), type="jpeg", quality=JPEG_Q)
            browser.close()
        ok, why = validate_jpeg(dest)
        if not ok:
            err(f"infografico: {why} — verificar template")
    cur = load_state(slug).get("stage")
    if cur not in ("aprovacao", "publicado"):
        save_state(slug, stage="render", slide_count=1)
    log(f"render OK: 1 imagem em {out}")


def cmd_render(args) -> None:
    ensure_not_published(args.slug)
    copy = load_json(slug_dir(args.slug) / "copy.json")
    formato = copy.get("formato") or "carrossel"
    out = slug_dir(args.slug)
    out.mkdir(parents=True, exist_ok=True)
    if formato == "infografico":
        _render_infografico(args.slug, copy, out)
        return
    slides = copy.get("slides")
    if not slides or not isinstance(slides, list):
        err("copy.json sem lista 'slides'")
    n = len(slides)
    if not 2 <= n <= 12:
        err(f"copy.json com {n} slides — esperado 6-8 (aceito 2-12)")
    tmpl = resolve_render_tokens(TEMPLATE.read_text()) if TEMPLATE.exists() else err(f"template não encontrado: {TEMPLATE}")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides, 1):
            dest = out / f"{i:02d}.jpg"
            ok, _ = validate_jpeg(dest)
            if ok:
                log(f"[checkpoint] slide {i} já renderizado e válido — pulando")
                continue
            log(f"renderizando slide {i}/{n}...")
            doc = (tmpl
                   .replace("{{titulo}}", html.escape(str(s.get("titulo", ""))))
                   .replace("{{corpo}}", html.escape(str(s.get("corpo", ""))))
                   .replace("{{numero}}", f"{i:02d} / {n:02d}"))
            page.set_content(doc, wait_until="load")
            page.screenshot(path=str(dest), type="jpeg", quality=JPEG_Q)
            ok, why = validate_jpeg(dest)
            if not ok:
                err(f"slide {i}: {why} — re-renderizei e falhou de novo; verificar template")
        browser.close()
    # re-render não rebaixa estágio já avançado (aprovacao/publicado)
    cur = load_state(args.slug).get("stage")
    if cur not in ("aprovacao", "publicado"):
        save_state(args.slug, stage="render", slide_count=n)
    log(f"render OK: {n} slides em {out}")


def cmd_package(args) -> None:
    ensure_not_published(args.slug)
    copy = load_json(slug_dir(args.slug) / "copy.json")
    formato = copy.get("formato") or "carrossel"
    out = slug_dir(args.slug)
    files = sorted(out.glob("*.jpg"))
    if not files:
        err("nenhum .jpg — rode render antes")
    if formato == "infografico" and len(files) != 1:
        err(f"infografico exige exatamente 1 .jpg — achou {len(files)}")
    for f in files:
        ok, why = validate_jpeg(f)
        if not ok:
            err(f"{f.name}: {why}")
    package = {
        "slug": args.slug,
        "formato": formato,
        "slides": [str(f) for f in files],
        "urls": [],
        "caption": copy.get("caption", ""),
        "alt_texts": copy.get("alt_texts", []),
        "source": copy.get("source", {}),
    }
    save_json(out / "package.json", package)
    save_state(args.slug, stage="aprovacao")
    log(f"package OK: {len(files)} imagem(ns) [{formato}] — aguardando aprovação")


def cmd_upload(args) -> None:
    ensure_not_published(args.slug)
    env = load_env()
    out = slug_dir(args.slug)
    package = load_json(out / "package.json") if (out / "package.json").exists() else None
    if not package:
        err("package.json não existe — rode package antes")
    sys.path.insert(0, str(Path(__file__).parent))
    from publishers import r2
    urls = r2.upload(env, args.slug, [Path(p) for p in package["slides"]])
    for u in urls:
        r2.validate_url(u)  # 200 + image/jpeg + sem redirect; falha => exit
    package["urls"] = urls
    save_json(out / "package.json", package)
    log(f"upload OK: {len(urls)} URLs validadas")
    for u in urls:
        log(u)


def cmd_publish(args) -> None:
    st = load_state(args.slug)
    if st.get("stage") != "aprovacao":
        err("estágio atual não permite publicar — precisa passar por package/upload (aprovacao)")
    env = load_env()
    package = load_json(slug_dir(args.slug) / "package.json")
    sys.path.insert(0, str(Path(__file__).parent))
    from publishers import meta
    res = meta.publish(package, env)
    if not res.get("ok"):
        err(f"publish falhou: {res.get('error')}")
    permalink = res.get("url")
    if not permalink:
        err("publish retornou ok sem permalink — tratado como falha")
    save_state(args.slug, stage="publicado", permalink=permalink,
               published_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
    log(f"publicado: {permalink}")


def cmd_status(args) -> None:
    st = load_state(args.slug)
    print(json.dumps(st, ensure_ascii=False, indent=2))


def cmd_validate(args) -> None:
    ok, why = validate_jpeg(Path(args.path))
    print(f"{'OK' if ok else 'FALHA'}: {args.path} — {why}")
    sys.exit(0 if ok else 1)


def cmd_convert(args) -> None:
    """Converte uma imagem (ex.: saída do image_generate) para 01.jpg 1080×1350 JPEG."""
    ensure_not_published(args.slug)
    src = Path(args.src)
    if not src.exists():
        err(f"imagem fonte não existe: {src}")
    from PIL import Image
    with Image.open(src) as im:
        rgb = im.convert("RGB")
    out = slug_dir(args.slug)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "01.jpg"
    fitted, mode = _fit_to(rgb, W, H)
    fitted.save(dest, "JPEG", quality=JPEG_Q)
    ok, why = validate_jpeg(dest)
    if not ok:
        err(f"convert falhou: {why}")
    log(f"convert OK: {src} -> {dest} (1080x1350 JPEG, {mode}, quality {JPEG_Q})")


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser(prog="pipeline.py", description="ig-posts: render/upload/package/publish/status")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("render", help="renderiza JPEGs 1080x1350 a partir de copy.json (checkpoint por slide)")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("package", help="monta package.json a partir de copy.json + JPEGs")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_package)

    p = sub.add_parser("upload", help="sobe JPEGs pro R2 e valida cada URL")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_upload)

    p = sub.add_parser("publish", help="publica via publishers/meta.py (Fase 4)")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_publish)

    p = sub.add_parser("status", help="mostra state.json")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("validate", help="valida um JPEG (exatamente 1080x1350, image/jpeg)")
    p.add_argument("path")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("convert", help="converte imagem para 01.jpg 1080x1350 (square=cover, 9:16=pad)")
    p.add_argument("slug")
    p.add_argument("--src", required=True, help="caminho da imagem fonte")
    p.set_defaults(fn=cmd_convert)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
