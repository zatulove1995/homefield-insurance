#!/usr/bin/env python3
"""Rasterize the Homefield brand mark (dark circle, blue house) to PNG/ICO.
Run from the repo root: python3 tools/make_brand_assets.py
Writes: assets/logo.png (512x512, white ground), assets/favicon-48.png,
assets/apple-touch-icon.png (180x180), favicon.ico (32x32 + 16x16), assets/favicon.svg"""
from PIL import Image, ImageDraw
import os

INK, BLUE, WHITE = (10, 13, 20, 255), (46, 91, 255, 255), (255, 255, 255, 255)
SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
       "<circle cx='16' cy='16' r='16' fill='#0A0D14'/>"
       "<path d='M9 9h14v8.5L16 25l-7-7.5z' fill='#2E5BFF'/></svg>")

def mark(size, ground=None, pad=0.0):
    """Draw the 32-unit mark scaled to `size`, supersampled 4x for clean edges."""
    S = size * 4
    img = Image.new("RGBA", (S, S), ground or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = S * (1 - 2 * pad) / 32.0          # one SVG unit in pixels
    o = S * pad                            # padding offset
    d.ellipse([o, o, o + 32 * u, o + 32 * u], fill=INK)
    pts = [(9, 9), (23, 9), (23, 17.5), (16, 25), (9, 17.5)]
    d.polygon([(o + x * u, o + y * u) for x, y in pts], fill=BLUE)
    return img.resize((size, size), Image.LANCZOS)

os.makedirs("assets", exist_ok=True)
mark(512, ground=WHITE, pad=0.08).convert("RGB").save("assets/logo.png", optimize=True)
mark(48).save("assets/favicon-48.png", optimize=True)
mark(180).save("assets/apple-touch-icon.png", optimize=True)
mark(32).save("favicon.ico", sizes=[(32, 32), (16, 16)])
with open("assets/favicon.svg", "w", encoding="utf-8") as f:
    f.write(SVG)
print("wrote assets/logo.png, assets/favicon-48.png, assets/apple-touch-icon.png, favicon.ico, assets/favicon.svg")
