#!/usr/bin/env python3
"""Render infografico.html -> 01.jpg (1080x1350, JPEG q90). Sem rede, sem credenciais."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
html_path = BASE / "infografico.html"
out_path = BASE / "01.jpg"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    page.goto(html_path.as_uri())
    page.wait_for_timeout(1500)  # fontes
    page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
    browser.close()

print(f"render OK: {out_path}")
