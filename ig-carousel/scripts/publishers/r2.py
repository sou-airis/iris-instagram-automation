"""publishers/r2.py — upload de JPEGs pro Cloudflare R2 + validação de URL.

Único lugar (junto com publishers/meta.py) com lógica de rede.
Credenciais vêm do dict env (lido de ~/.hermes/.env pelo pipeline.py).
Nada de segredo é logado.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONTENT_TYPE = "image/jpeg"
PREFIX = "ig"  # chave S3: ig/<slug>/NN.jpg


def upload(env: dict, slug: str, files: list[Path]) -> list[str]:
    """Sobe os JPEGs e devolve as URLs públicas na mesma ordem."""
    import boto3
    from botocore.config import Config

    client = boto3.client(
        "s3",
        endpoint_url=env["R2_ENDPOINT"],
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    bucket = env["R2_BUCKET"]
    base = env["R2_PUBLIC_URL"].rstrip("/")
    urls: list[str] = []
    for f in files:
        key = f"{PREFIX}/{slug}/{f.name}"
        with open(f, "rb") as body:
            client.put_object(Bucket=bucket, Key=key, Body=body, ContentType=CONTENT_TYPE)
        urls.append(f"{base}/{key}")
    return urls


def validate_url(url: str) -> None:
    """curl -I: exige 200, image/jpeg e sem redirect. Falha => sys.exit."""
    r = subprocess.run(
        ["curl", "-sI", "--max-time", "20", url],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"ERRO: curl falhou em {url}: {r.stderr.strip() or r.returncode}")
    lines = [ln.strip().lower() for ln in r.stdout.splitlines() if ln.strip()]
    if not lines:
        sys.exit(f"ERRO: resposta vazia de {url}")
    status_line = lines[0]
    if " 200 " not in f" {status_line} " and not status_line.startswith("http/2 200"):
        sys.exit(f"ERRO: {url} -> {status_line}")
    ctype = next((ln for ln in lines if ln.startswith("content-type:")), "")
    if CONTENT_TYPE not in ctype:
        sys.exit(f"ERRO: {url} content-type inesperado: {ctype or 'ausente'}")
    if any(ln.startswith("location:") for ln in lines):
        sys.exit(f"ERRO: {url} respondeu com redirect — bucket com acesso r2.dev público?")
    print(f"OK {url} (200, image/jpeg, sem redirect)", flush=True)
