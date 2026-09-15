#!/usr/bin/env python3
"""
Generate a WhatsApp-shareable price-list image from the Techno ledger.
Only items EN STOCK, only sell prices (never provider costs).

Usage:
  python tools/techno_whatsapp_catalog.py            # → .tmp/techno_catalogo_YYYYMMDD.png
"""
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sheets_client import get_services
from techno_ledger import get_sheet_id, rows

W = 1080
BG = (10, 10, 12)
FG = (240, 240, 245)
ACCENT = (10, 132, 255)
DIM = (130, 130, 140)


def font(size, bold=False):
    name = "HelveticaNeue.ttc"
    try:
        return ImageFont.truetype(f"/System/Library/Fonts/{name}", size, index=1 if bold else 0)
    except OSError:
        return ImageFont.load_default(size)


def main():
    sheets, _ = get_services()
    sid = get_sheet_id()
    if not sid:
        sys.exit("No hay ledger. Corré: python tools/techno_ledger.py setup")
    stock = [r + [""] * (9 - len(r)) for r in rows(sheets, sid)]
    stock = [r for r in stock if r[4] == "EN STOCK"]
    if not stock:
        sys.exit("No hay items en stock")

    row_h, top, bottom = 86, 290, 200
    H = top + len(stock) * row_h + bottom
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((70, 80), "TECHNO APPLE", font=font(64, bold=True), fill=FG)
    d.text((70, 165), "Olavarría · Garantía · Sellados", font=font(30), fill=DIM)
    d.line([(70, 240), (W - 70, 240)], fill=ACCENT, width=4)

    y = top
    for r in stock:
        d.text((70, y), r[1], font=font(36), fill=FG)
        price = f"USD {float(r[3]):,.0f}".replace(",", ".")
        d.text((W - 70, y), price, font=font(36, bold=True), fill=ACCENT, anchor="ra")
        d.line([(70, y + 60), (W - 70, y + 60)], fill=(30, 30, 36), width=1)
        y += row_h

    d.text((70, y + 30), "Consultá stock y reservá por este WhatsApp", font=font(30), fill=FG)
    d.text((70, y + 80), f"Precios al {date.today():%d/%m/%Y} · Aceptamos pesos al blue", font=font(26), fill=DIM)

    out = ROOT / ".tmp" / f"techno_catalogo_{date.today():%Y%m%d}.png"
    out.parent.mkdir(exist_ok=True)
    img.save(out)
    print(f"Wrote {out} ({len(stock)} items)")


if __name__ == "__main__":
    main()
