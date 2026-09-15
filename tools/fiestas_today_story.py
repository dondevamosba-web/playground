#!/usr/bin/env python3
"""
Daily "HOY 🎉" story for Fiestas: lists tonight's events from the Queue sheet
(any status except skipped/expired, event date == today, with venue or lineup),
renders a 1080x1920 story in the violet brand style and publishes it.

Exits silently if there are no events today. Runs daily 11:00 via launchd.

Usage:
  python3 tools/fiestas_today_story.py [--dry-run]
"""
import argparse
import io
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.fiestas_card import ACCENT, ACCENT_DEEP, BLACK, WHITE, HANDLE, FONT_DIN, FONT_ARIAL, f

AR = timezone(timedelta(hours=-3))
W, H = 1080, 1920
GRAPH = "https://graph.facebook.com/v19.0"


def ra_date(source_url):
    """Real event date from RA (queue sheet dates have proven unreliable)."""
    import re
    m = re.search(r"ra\.co/events/(\d+)", source_url or "")
    if not m:
        return None
    try:
        from tools.scrape_ra_events import RA_GRAPHQL, HEADERS
        r = requests.post(RA_GRAPHQL, headers=HEADERS, timeout=15, json={
            "query": "query($id: ID!) { event(id: $id) { date } }",
            "variables": {"id": m.group(1)}})
        return ((r.json().get("data") or {}).get("event") or {}).get("date", "")[:10]
    except Exception:
        return None


def todays_events(sheets):
    fid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=fid, range="Queue!A2:M500").execute().get("values", [])
    today = datetime.now(AR).strftime("%Y-%m-%d")
    evs, seen = [], set()
    for r in rows:
        g = lambda j: r[j].strip() if len(r) > j else ""
        if g(3) != today or g(11) in ("skipped", "expired"):
            continue
        if not g(4) and not g(6):
            continue  # ghosts
        real = ra_date(g(10))
        if real and real != today:
            print(f"  [fecha] {g(2)[:40]}: sheet dice hoy pero RA dice {real} — salteado")
            continue
        key = g(2)[:35].lower()
        if key in seen:
            continue
        seen.add(key)
        evs.append({"name": g(2), "venue": g(4).split(",")[0], "lineup": g(6).split(",")[0]})
    return evs[:6]


def render(evs):
    img = Image.new("RGB", (W, H), BLACK)
    glow = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(glow)
    d.ellipse([W // 2 - 500, 300, W // 2 + 500, 1300], fill=ACCENT_DEEP)
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220)), 0.9)
    d = ImageDraw.Draw(img)

    chip = "FIESTAS ELECTRÓNICAS"
    cf = f(FONT_DIN, 52)
    tw = d.textlength(chip, font=cf)
    d.rectangle([(W - tw - 52) / 2, 120, (W + tw + 52) / 2, 196], fill=ACCENT)
    d.text((W / 2, 186), chip, font=cf, fill=BLACK, anchor="mb")

    hoy = datetime.now(AR)
    dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    d.text((W / 2, 320), "HOY SALE", font=f(FONT_DIN, 130), fill=WHITE, anchor="mm")
    d.text((W / 2, 420), f"{dias[hoy.weekday()]} {hoy.day:02d}.{hoy.month:02d}", font=f(FONT_DIN, 60), fill=ACCENT, anchor="mm")

    y = 560
    for ev in evs:
        name = ev["name"][:32].upper()
        d.text((80, y), name, font=f(FONT_DIN, 76), fill=WHITE)
        info = " · ".join(x for x in (ev["venue"], ev["lineup"]) if x)[:45]
        if info:
            d.text((80, y + 78), info, font=f(FONT_DIN, 46), fill=ACCENT)
            y += 190
        else:
            y += 130
        d.line([(80, y - 28), (W - 80, y - 28)], fill=(60, 40, 90), width=2)

    d.text((W / 2, H - 120), "info completa en el feed", font=f(FONT_ARIAL, 34), fill=(200, 200, 210), anchor="mm")
    d.text((W / 2, H - 60), HANDLE, font=f(FONT_ARIAL, 30), fill=(255, 255, 255), anchor="mm")

    out = ROOT / ".tmp" / f"fiestas_hoy_{hoy:%Y%m%d}.jpg"
    img.save(out, quality=92)
    return out


def publish(path):
    sys.path.insert(0, str(ROOT / "tools"))
    from upload_to_drive import get_drive_service
    from googleapiclient.http import MediaFileUpload
    drive = get_drive_service()
    meta = {"name": path.name}
    media = MediaFileUpload(str(path), mimetype="image/jpeg")
    fid = drive.files().create(body=meta, media_body=media, fields="id").execute()["id"]
    drive.permissions().create(fileId=fid, body={"role": "reader", "type": "anyone"}).execute()
    url = f"https://drive.google.com/uc?export=download&id={fid}"

    ig_id = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    r = requests.post(f"{GRAPH}/{ig_id}/media", data={
        "image_url": url, "media_type": "STORIES", "access_token": token}).json()
    if "id" not in r:
        print(f"ERROR container: {r}")
        return None
    time.sleep(2)
    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish", data={
        "creation_id": r["id"], "access_token": token}).json()
    return r2.get("id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sheets, _ = get_services()
    evs = todays_events(sheets)
    if not evs:
        print("sin eventos hoy — nada que publicar")
        return
    path = render(evs)
    print(f"{len(evs)} eventos hoy → {path}")
    if a.dry_run:
        print("[dry-run] no publico")
        return
    sid = publish(path)
    print(f"story: {sid or 'FALLÓ'}")


if __name__ == "__main__":
    main()
