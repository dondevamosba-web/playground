#!/usr/bin/env python3
"""
Generate branded 1080x1080 product cards for @techno.apple.ok.

Two layouts:
  - PHOTO card: product image fills top 65%, black bar at bottom with name + footer
  - TEXT card: full black, large product name centered, caption excerpt

Updates Media URL (col I) in the Techno sheet for all pending rows.

Usage:
  python3 tools/generate_techno_cards.py
  python3 tools/generate_techno_cards.py --dry-run
"""

import argparse
import io
import json
import os
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

IMAGE_CACHE_PATH = ROOT / ".tmp" / "techno_image_cache.json"

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"

W, H = 1080, 1080
BG        = (8, 8, 10)
FG        = (240, 240, 245)
ACCENT    = (10, 132, 255)     # Apple blue
DIM       = (140, 140, 150)
GREEN     = (34, 197, 94)      # green accent bar

OUT_DIR = ROOT / ".tmp" / "techno_cards"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for name in ("HelveticaNeue.ttc", "Arial Bold.ttf", "Arial.ttf"):
        path = f"/System/Library/Fonts/{name}"
        try:
            idx = 1 if bold and name.endswith(".ttc") else 0
            return ImageFont.truetype(path, size, index=idx)
        except OSError:
            continue
    return ImageFont.load_default(size)


def fetch_image(url: str) -> Image.Image | None:
    if not url or not url.startswith("http"):
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except Exception:
        return None


def lookup_image_from_cache(product: str) -> Image.Image | None:
    if not IMAGE_CACHE_PATH.exists():
        return None
    cache = json.loads(IMAGE_CACHE_PATH.read_text())
    # Try to find product in cache by matching product name against keys (format brand::product)
    product_lower = product.lower()
    for key, urls in cache.items():
        cached_product = key.split("::", 1)[-1].lower()
        if not urls:
            continue
        if cached_product in product_lower or product_lower in cached_product:
            img = fetch_image(urls[0])
            if img:
                return img
    return None


def wrap_text(d: ImageDraw.ImageDraw, text: str, x: int, y: int, max_w: int,
              fnt: ImageFont.FreeTypeFont, fill, line_spacing: int = 8) -> int:
    """Draw wrapped text, return final y position."""
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if d.textlength(test, font=fnt) > max_w and line:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + line_spacing
    return y


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40]


def make_photo_card(product: str, caption: str, photo: Image.Image, row: int) -> Path:
    """Product photo top 65%, black bar bottom 35% with name + footer."""
    card = Image.new("RGB", (W, H), BG)

    # --- product photo ---
    photo_h = int(H * 0.65)
    photo_rgb = photo.convert("RGB")
    # fit inside top area, center-crop
    ratio = max(W / photo_rgb.width, photo_h / photo_rgb.height)
    nw = int(photo_rgb.width * ratio)
    nh = int(photo_rgb.height * ratio)
    photo_rgb = photo_rgb.resize((nw, nh), Image.LANCZOS)
    ox = (nw - W) // 2
    oy = (nh - photo_h) // 2
    card.paste(photo_rgb.crop((ox, oy, ox + W, oy + photo_h)), (0, 0))

    # gradient fade at bottom of photo into black
    fade = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(160):
        alpha = int(255 * (i / 160) ** 1.5)
        fd.line([(0, i), (W, i)], fill=(8, 8, 10, alpha))
    card.paste(fade.convert("RGB"), (0, photo_h - 160), mask=fade.split()[3])

    d = ImageDraw.Draw(card)

    # --- green accent bar ---
    d.rectangle([(0, photo_h), (W, photo_h + 3)], fill=GREEN)

    # --- bottom text area ---
    pad = 54
    y = photo_h + 20

    # header line: TECHNO APPLE
    d.text((pad, y), "TECHNO APPLE", font=font(28, bold=True), fill=ACCENT)
    handle_x = W - pad - d.textlength("@techno.apple.ok", font=font(22))
    d.text((handle_x, y + 3), "@techno.apple.ok", font=font(22), fill=DIM)
    y += 46

    # product name — large bold
    name_font = font(48, bold=True)
    y = wrap_text(d, product, pad, y, W - pad * 2, name_font, FG, line_spacing=4)
    y += 10

    # caption excerpt — 2 lines max
    excerpt = caption[:120].rsplit(" ", 1)[0] + "…" if len(caption) > 120 else caption
    y = wrap_text(d, excerpt, pad, y, W - pad * 2, font(26), DIM, line_spacing=4)

    # footer
    footer_y = H - 48
    d.text((pad, footer_y), "Importado desde USA · Olavarría · Envíos CABA",
           font=font(22), fill=DIM)

    out = OUT_DIR / f"t{row:03d}_{slug(product)}_card.png"
    card.save(out, optimize=True)
    return out


def make_text_card(product: str, caption: str, row: int) -> Path:
    """Full black card with large product name + excerpt — style from feed."""
    card = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(card)

    # top accent bar
    d.rectangle([(0, 0), (W, 4)], fill=GREEN)

    pad = 70

    # header
    header_y = 68
    d.text((pad, header_y), "TECHNO APPLE", font=font(48, bold=True), fill=FG)
    d.text((pad, header_y + 62), "@techno.apple.ok", font=font(30), fill=DIM)

    # separator line
    sep_y = header_y + 118
    d.line([(pad, sep_y), (W - pad, sep_y)], fill=ACCENT, width=3)

    # product name — very large, centered vertically in remaining space
    name_font = font(72, bold=True)
    # estimate height for product name (2 lines max)
    name_words = product.split()
    name_lines = []
    line = []
    for w in name_words:
        test = " ".join(line + [w])
        if d.textlength(test, font=name_font) > W - pad * 2 and line:
            name_lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        name_lines.append(" ".join(line))

    total_name_h = len(name_lines) * (72 + 8)
    caption_lines = textwrap.wrap(caption[:200], width=42)[:4]
    total_caption_h = len(caption_lines) * (32 + 6)
    block_h = total_name_h + 40 + total_caption_h
    y = sep_y + 40 + (H - sep_y - 40 - block_h - 80) // 2

    for ln in name_lines:
        d.text((pad, y), ln, font=name_font, fill=FG)
        y += 72 + 8
    y += 30

    for ln in caption_lines:
        d.text((pad, y), ln, font=font(30), fill=DIM)
        y += 30 + 6

    # bottom
    footer_y = H - 60
    d.rectangle([(0, footer_y - 4), (W, footer_y - 1)], fill=ACCENT)
    d.text((pad, footer_y), "Importado desde USA · Garantía · Olavarría",
           font=font(24), fill=DIM)

    out = OUT_DIR / f"t{row:03d}_{slug(product)}_text.png"
    card.save(out, optimize=True)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets, _ = get_services()
    sid = os.getenv(SHEET_ENV_KEY)

    result = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="A2:K400"
    ).execute()
    rows = result.get("values", [])

    updates = []
    for i, row in enumerate(rows):
        sheet_row = i + 2
        status  = row[9].strip() if len(row) > 9 else ""
        product = row[3].strip() if len(row) > 3 else ""
        caption = row[6].strip() if len(row) > 6 else ""
        media   = row[8].strip() if len(row) > 8 else ""

        if status == "posted" or not product:
            continue
        # skip if already has a local card we generated
        if media and ".tmp/techno_cards/" in media:
            continue

        print(f"  [{sheet_row:3d}] {product[:45]}", end="", flush=True)

        # 1. Try image URL from sheet
        photo = fetch_image(media) if media else None

        # 2. Fallback: look up in image cache by product name
        if not photo:
            photo = lookup_image_from_cache(product)

        if photo:
            out = make_photo_card(product, caption, photo, sheet_row)
            print(f" → photo card")
        else:
            # No image found — skip rather than generate a text-only card
            print(f" → SKIP (no image)")
            continue

        local_path = str(out)
        updates.append({"range": f"I{sheet_row}", "values": [[local_path]]})

    print(f"\n{len(updates)} cards generated in {OUT_DIR}")

    if args.dry_run or not updates:
        return

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": updates},
    ).execute()
    print("Sheet updated.")


if __name__ == "__main__":
    main()
