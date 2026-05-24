#!/usr/bin/env python3
"""Extract images from Moschato PDF — both embedded raw and full-page renders."""
import fitz
import os
from pathlib import Path

BASE = Path(__file__).parent
PDF = BASE.parent / "Eleftheriou Venizelou 90 - Moschato 2nd & 3rd.pdf"
RAW_DIR = BASE / "img" / "raw_embedded"
PAGE_DIR = BASE / "img" / "raw_pages"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PAGE_DIR.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF)
print(f"Opened PDF: {len(doc)} pages")

# 1) Embedded raw images (orijinal raster çözünürlüğü)
seen = set()
for pno in range(len(doc)):
    page = doc[pno]
    for idx, info in enumerate(page.get_images(full=True)):
        xref = info[0]
        if xref in seen:
            continue
        seen.add(xref)
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.colorspace and pix.colorspace.name not in ("DeviceRGB", "DeviceGray"):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            if pix.alpha:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            w, h = pix.width, pix.height
            if w < 200 or h < 200:
                continue  # küçükleri atla (ikonlar, dekoratif çizgiler)
            out = RAW_DIR / f"p{pno+1:02d}_x{xref}_{w}x{h}.jpg"
            pix.save(out, jpg_quality=92)
            print(f"  embedded p{pno+1} x{xref}: {w}x{h} -> {out.name}")
        except Exception as e:
            print(f"  err p{pno+1} x{xref}: {e}")

# 2) Full-page render (300 DPI) — kritik sayfalar için kompozisyon önemli olabilir
KEY_PAGES = [3, 4, 5, 6, 7, 12, 33, 51, 52]
zoom = 300 / 72
mat = fitz.Matrix(zoom, zoom)
for pno in KEY_PAGES:
    if pno > len(doc):
        continue
    page = doc[pno - 1]
    pix = page.get_pixmap(matrix=mat, alpha=False)
    out = PAGE_DIR / f"page_{pno:02d}.jpg"
    pix.save(out, jpg_quality=88)
    print(f"  page render p{pno}: {pix.width}x{pix.height} -> {out.name}")

doc.close()
print(f"\nDone. {len(seen)} unique embedded images. {len(KEY_PAGES)} page renders.")
