#!/usr/bin/env python3
"""
Create or update the Techno (@techno.apple.ok) content calendar in Google Sheets.
Picks products from techno_catalog.json using weighted selection.
No price required — posts use WhatsApp CTA.

Usage:
  python3 tools/fill_content_techno.py              # 4 weeks from today
  python3 tools/fill_content_techno.py --weeks 8
  python3 tools/fill_content_techno.py --dry-run
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.claude_call import call_claude

SHEET_TITLE   = "Techno — Content Calendar"
SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"
CATALOG_PATH  = ROOT / "tools" / "techno_catalog.json"

HASHTAGS_BASE = (
    "#Olavarría #OlavarríaTech #TecnologíaOlavarría #importadoUSA "
    "#directoDeUSA #technoAppleOk #gadgets #argentina #tech"
)

BRAND_HASHTAGS = {
    "apple":       "#apple #iphone #ios #applefan #manzanita",
    "samsung":     "#samsung #galaxy #android #samsungfan",
    "playstation": "#playstation #ps5 #gaming #gamer #sonyplaystation",
}


def load_catalog() -> dict:
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_recently_posted(sheets, sheet_id: str, days: int = 21) -> set:
    """Return product names posted in the last N days."""
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:K500"
    ).execute().get("values", [])
    posted = set()
    for r in rows:
        status = r[9].strip() if len(r) > 9 else ""
        d = r[0].strip() if r else ""
        name = r[3].strip() if len(r) > 3 else ""
        if status == "posted" and d >= cutoff and name:
            posted.add(name)
    return posted


def pick_product(products: list, used: list, skip_names: set = None) -> dict:
    """Weighted random pick, avoids same brand twice in a row and recently-posted products."""
    skip_names = skip_names or set()
    last_brand = used[-1]["brand"] if used else None
    # Exclude recently posted and same brand in a row; fall back to just skip_names if needed
    pool = [p for p in products
            if p["brand"] != last_brand and p.get("product", p["brand"]) not in skip_names]
    if not pool:
        pool = [p for p in products if p.get("product", p["brand"]) not in skip_names]
    if not pool:
        pool = products  # last resort
    weights = [p["weight"] for p in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def generate_caption(product: dict, aesthetic: dict) -> str:
    brand = product["brand"]
    style = aesthetic[brand]
    whatsapp = os.getenv("TECHNO_WHATSAPP", "")
    wa_link = f"https://wa.me/{whatsapp.lstrip('+').replace(' ', '')}" if whatsapp else "WhatsApp"

    if product["type"] == "meme":
        prompt = f"""Escribí un post meme para Instagram de @techno.apple.ok sobre la marca {brand.capitalize()}.
Contexto: tienda en Olavarría que importa equipos directo desde USA.
Tono: {style['tone']}
Reglas: humor relatable sobre tecnología o ser fan de la marca, sin precio, máximo 60 palabras, sin emojis al inicio, no empieces con ¿
Devolvé solo el caption."""
    else:
        prompt = f"""Escribí un caption para Instagram de @techno.apple.ok.
Producto: {product.get('product', brand.capitalize())}
Tipo: {product['type']}
Tono: {style['tone']}
CTA: {style['cta']} → {wa_link}

Contexto clave que debe sentirse en el texto:
- Importamos directo desde USA a Olavarría
- Llegás al equipo antes que al retail local
- Sin intermediarios, precio justo
- Equipos con garantía

Reglas:
- Máximo 80 palabras
- Primera línea: gancho fuerte (sin emojis, no empieces con ¿)
- Mencioná el producto por nombre
- Incluí la idea de "directo de USA" o "importado" de forma natural, no forzada
- CTA al WhatsApp al final
- Sin precio (el cliente pregunta por WhatsApp)
- Español rioplatense (vos, no usted)

Devolvé solo el caption, sin comillas."""

    for attempt in range(3):
        try:
            result = call_claude(prompt, model="haiku")
            time.sleep(0.4)
            return result
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 5
                print(f"    ⚠ Retry {attempt+1} after {wait}s ({e})")
                time.sleep(wait)
            else:
                raise


def build_rows(start: date, weeks: int, catalog: dict, dry_run: bool,
               recently_posted: set = None) -> list[list]:
    products = catalog["products"]
    slots = catalog["schedule"]["slots"]
    aesthetic = catalog["aesthetic"]
    recently_posted = recently_posted or set()
    used = []
    rows = []

    # Build (date, time) pairs day-by-day
    schedule_pairs = []
    for day_offset in range(weeks * 7):
        current_day = start + timedelta(days=day_offset)
        day_slots = [s["time"] for s in slots if s["weekday"] == current_day.weekday()]
        for t in day_slots:
            schedule_pairs.append((current_day, t))

    # Products to skip: recently posted + already queued this run
    skip_names = set(recently_posted)

    for post_date, time_str in schedule_pairs:
        product = pick_product(products, used, skip_names=skip_names)
        used.append(product)
        # Add to skip so the same product doesn't appear twice in this batch
        skip_names.add(product.get("product", product["brand"]))

        if dry_run:
            caption = f"[{product['type'].upper()}] {product.get('product', product['brand'])}"
        else:
            label = product.get('product') or product['brand']
            print(f"  [{post_date} {time_str}] {label} ({product['type']})...")
            caption = generate_caption(product, aesthetic)

        brand_tags = BRAND_HASHTAGS.get(product["brand"], "")
        hashtags = f"{brand_tags} {HASHTAGS_BASE}".strip()

        rows.append([
            post_date.isoformat(),
            time_str,
            post_date.strftime("%A"),
            product.get("product", product["brand"]),
            product["brand"],
            product["type"],
            caption,
            hashtags,
            "",         # Media URL — user fills this
            "pending",
            "",         # Post ID
        ])

    rows.sort(key=lambda r: r[0] + r[1])
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks",    type=int, default=4)
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--sheet-id", help="Override sheet ID")
    args = parser.parse_args()

    catalog = load_catalog()
    start = date.today() + timedelta(days=1)
    total = args.weeks * len(catalog["schedule"]["slots"])

    sheets, drive = get_services()
    sheet_id = args.sheet_id or os.getenv(SHEET_ENV_KEY)

    recently_posted = set()
    if sheet_id and not args.dry_run:
        recently_posted = get_recently_posted(sheets, sheet_id)
        if recently_posted:
            print(f"Skipping {len(recently_posted)} recently-posted products.")

    print(f"Generating {total} posts over {args.weeks} weeks (from {start})...")
    rows = build_rows(start, args.weeks, catalog, args.dry_run, recently_posted)

    if args.dry_run:
        print("\n── Preview ─────────────────────────────────────────────")
        for r in rows:
            print(f"  {r[0]} {r[1]}  [{r[5]}] {r[4].upper()} — {r[3]}")
            print(f"    {r[6][:80]}")
        print(f"\n  Total: {len(rows)} posts")
        return

    if not sheet_id:
        print(f"Creating Google Sheet: '{SHEET_TITLE}'...")
        f = drive.files().create(
            body={"name": SHEET_TITLE, "mimeType": "application/vnd.google-apps.spreadsheet"},
            fields="id",
        ).execute()
        sheet_id = f["id"]

        env_path = ROOT / ".env"
        content = env_path.read_text()
        if SHEET_ENV_KEY + "=" in content:
            lines = [
                f"{SHEET_ENV_KEY}={sheet_id}" if l.startswith(SHEET_ENV_KEY + "=") else l
                for l in content.splitlines()
            ]
            env_path.write_text("\n".join(lines) + "\n")
        else:
            with open(env_path, "a") as f2:
                f2.write(f"\n{SHEET_ENV_KEY}={sheet_id}\n")
        print(f"  Sheet ID saved to .env")

    header = [[
        "Date", "Time", "Day", "Product", "Brand", "Post Type",
        "Caption", "Hashtags", "Media URL", "Status", "Post ID",
    ]]

    existing = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A1:A1"
    ).execute().get("values", [])

    if not existing:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="A1",
            valueInputOption="RAW",
            body={"values": header},
        ).execute()

    sheets.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()

    print(f"\nDone! https://docs.google.com/spreadsheets/d/{sheet_id}")
    print("\nNext: add Media URLs to each row, then run:")
    print("  python3 tools/auto_post_techno.py")


if __name__ == "__main__":
    main()
