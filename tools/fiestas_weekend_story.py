#!/usr/bin/env python3
"""
"Este finde" story (1080×1920) for @fiestaselectronicasbuenosaires:
lists Fri–Sun events from the RA scraper output, brand teal-on-black style.

Usage:
  python3 tools/fiestas_weekend_story.py             # render only
  python3 tools/fiestas_weekend_story.py --publish   # render + post as story
Events come from the fiestas Queue sheet (always fresh); brand violet style.
Output: .tmp/fiestas_finde_<sat-date>.png
"""
import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
FONT_DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
import sys
sys.path.insert(0, str(ROOT))
from tools.fiestas_card import ACCENT  # violeta de marca (Guido rechazó el teal)
TEAL = ACCENT
WHITE = (255, 255, 255)
DIM = (160, 160, 165)
W, H = 1080, 1920
DIAS = {4: "VIERNES", 5: "SÁBADO", 6: "DOMINGO"}


def next_weekend():
    today = date.today()
    fri = today + timedelta((4 - today.weekday()) % 7)
    if today.weekday() in (5, 6):  # already in the weekend → use current one
        fri = today - timedelta(today.weekday() - 4)
    return fri, fri + timedelta(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true", help="post the story to IG")
    a = ap.parse_args()

    # events from the fiestas Queue sheet — always current, any status except junk
    import os
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
    from tools.sheets_client import get_services
    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=os.environ["FIESTAS_APPROVAL_SHEET_ID"],
        range="Queue!A2:N500").execute().get("values", [])
    events, seen = [], []
    for r in rows:
        name = (r[2] if len(r) > 2 else "").strip()
        status = (r[11] if len(r) > 11 else "").strip()
        if not name or status in ("skipped", "duplicate", "dup-skip", "vencida"):
            continue
        key = name[:20].lower()
        # loose dedupe: skip if this name overlaps an already-kept one
        # (same real event scraped twice under a longer/shorter title)
        if any(key in s or s in key for s in seen):
            continue
        seen.append(key)
        events.append({
            "name": name,
            "date": (r[3] if len(r) > 3 else ""),
            "venue": (r[4] if len(r) > 4 else ""),
            "artists": [x.strip() for x in (r[6] if len(r) > 6 else "").split(",") if x.strip()],
            "time": "",
        })
    fri, sun = next_weekend()
    finde = []
    for e in events:
        try:
            d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if fri <= d <= sun:
            finde.append((d, e))
    if not finde:
        raise SystemExit(f"No hay eventos entre {fri} y {sun} en {a.input} — refrescar con scrape_ra_events.py")
    finde.sort(key=lambda x: (x[0], x[1].get("time", "")))

    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    def f(path, s):
        for candidate in (path, "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
            try:
                return ImageFont.truetype(candidate, s)
            except OSError:
                continue
        return ImageFont.load_default(s)

    def fit_font(path, text, max_size, min_size, max_width):
        """Shrink font size until `text` fits max_width; never truncate by char count."""
        size = max_size
        while size > min_size:
            font = f(path, size)
            if d.textlength(text, font=font) <= max_width:
                return font
            size -= 4
        return f(path, min_size)

    # header
    d.rectangle([(52, 100), (52 + 320, 152)], fill=TEAL)
    d.text((68, 104), "ESTE FINDE", font=f(FONT_DIN, 42), fill=(0, 0, 0))
    d.text((60, 190), f"{fri:%d/%m} — {sun:%d/%m}", font=f(FONT_DIN, 110), fill=WHITE)
    d.rectangle([(60, 330), (W - 60, 333)], fill=TEAL)

    MAX_TEXT_WIDTH = W - 120  # 60px margin each side
    FOOTER_TOP = H - 220      # nothing may draw below this

    y, last_day = 400, None
    for ev_date, e in finde:
        if y > FOOTER_TOP - 90:  # not enough room left for even a compact entry
            break
        if ev_date.weekday() != last_day:
            if y > FOOTER_TOP - 150:
                break
            d.text((60, y), DIAS.get(ev_date.weekday(), str(ev_date)), font=f(FONT_DIN, 54), fill=TEAL)
            y += 78
            last_day = ev_date.weekday()
        artists = ", ".join(e.get("artists") or []) or e["name"]
        venue = (e.get("venue") or "").removeprefix("TBA - ").removeprefix("TBA-").strip()
        title_font = fit_font(FONT_DIN, artists.upper(), max_size=64, min_size=34, max_width=MAX_TEXT_WIDTH)
        d.text((60, y), artists.upper(), font=title_font, fill=WHITE)
        y += 72
        if venue:
            info = f"{venue} · {e['time']}h" if e.get("time") else venue
            venue_font = fit_font(FONT_ARIAL, info, max_size=28, min_size=20, max_width=MAX_TEXT_WIDTH)
            d.text((60, y), info, font=venue_font, fill=DIM)
        y += 86

    d.rectangle([(60, H - 200), (W - 60, H - 197)], fill=TEAL)
    d.text((60, H - 160), "INFO Y ENTRADAS EN NUESTRA BIO", font=f(FONT_ARIAL, 30), fill=WHITE)
    d.text((60, H - 110), "@fiestaselectronicasbuenosaires", font=f(FONT_ARIAL, 26), fill=DIM)

    out = ROOT / ".tmp" / f"fiestas_finde_{fri + timedelta(1):%Y%m%d}.png"
    img.save(out)
    print(f"Wrote {out} ({len(finde)} eventos {fri} → {sun})")

    if a.publish:
        from tools.publish_story import upload_to_drive, post_story
        url = upload_to_drive(out.read_bytes(), out.name)
        mid = post_story(os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"], url)
        print(f"Story publicada: {mid}" if mid else "STORY ERROR")


if __name__ == "__main__":
    main()
