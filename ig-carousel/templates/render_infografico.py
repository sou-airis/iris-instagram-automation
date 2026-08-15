#!/usr/bin/env python3
"""Render infografico-guia.html -> 01.jpg (1080x1350, JPEG q90).

Uso: python render_infografico.py [--out DIR] [--html PATH]
- Padrão: html = templates/infografico-guia.html; out = próprio diretório.
- Tokens {{FONTS_DIR}}/{{ASSETS_DIR}} resolvidos no momento do render
  (templates commitados ficam sem paths do servidor — gate pre-push).
- robot.png (mascote) deve estar no --out (colocado pelo agente).
Sem rede, sem credenciais.
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent  # templates/
SKILL_ROOT = BASE.parent                # ig-carousel/
ASSETS_DIR = SKILL_ROOT / "assets"
FONTS_DIR = Path.home() / ".fonts"


def resolve(t: str) -> str:
    return (t.replace("{{FONTS_DIR}}", FONTS_DIR.as_uri())
             .replace("{{ASSETS_DIR}}", ASSETS_DIR.as_uri()))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(BASE))
    ap.add_argument("--html", default=str(BASE / "infografico-guia.html"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = resolve(Path(args.html).read_text())
    html_out = out / "infografico.html"
    html_out.write_text(doc)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        page.goto(html_out.as_uri())
        page.wait_for_timeout(1500)
        page.screenshot(path=str(out / "01.jpg"),
                        clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
        browser.close()
    print(f"render OK: {out / '01.jpg'}")


if __name__ == "__main__":
    main()
