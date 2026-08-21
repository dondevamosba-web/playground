#!/usr/bin/env python3
"""
Auto-queue Fiestas posts from two sources:
  1. RA queue sheet (events scraped daily by queue_event_posts.py)
  2. 11 IG source accounts (scraped live via IG unofficial API)

Generates branded 1080x1080 images, uploads to Drive, and adds to the
unified approval sheet as "approved" with 4-5 time slots per day.

Skips: past events, already-queued posts, junk/noise events.
Prioritizes: big venues, events within 21 days.

Usage:
  python3 tools/auto_fiestas_queue.py            # RA + all IG sources
  python3 tools/auto_fiestas_queue.py --ra-only  # skip IG scraping
  python3 tools/auto_fiestas_queue.py --dry-run  # preview without writing
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools import ig_fetch

QUEUE_SHEET   = "1eZxvQyhU_wBRRbF_ACPHufybg4JOv0mL_DfKGoXhOd0"
UNIFIED_SHEET = os.environ["UNIFIED_APPROVAL_SHEET_ID"]
AR_TZ         = timezone(timedelta(hours=-3))

# IG accounts to scrape for events
IG_SOURCES = [
    "electronicmusictickets",
    "infoticketsarg",
    "baires.electronica",
    "technobuenosaires",
    "wearebombo",
    "ems_arg",
    "moonparkoficial",
    "nisfernandez",
]

# IG accounts for viral rave culture content (no event date required)
IG_VIRAL_SOURCES = [
    "mixmag",
    "technomistery_",
    "rave.archive",
    "ravehistory",
    "techno.community",
    "underground.techno",
    "djmag",
    "boilerroom",
    "residentadvisor",
    "xlr8r",
    "electronicbeats",
    "factmag",
    "ra_co",
    "fabriclondon",
    "electronicmusicarg",
    "ravediary",
    "technoarchive_",
    "scenelatina",
]

VIRAL_KW = re.compile(
    r"\b(rave|techno|house|dj|electronic|acid|underground|goa|ibiza|berghain|"
    r"carl.?cox|prodigy|daft.?punk|tomorrowland|burning.?man|historia|history|"
    r"años 9|the 9|años 8|illegal|penaliz|criminal|castillo|castle|cultura|"
    r"open.to.close|set|mix|reel|viral|archive|footage)\b",
    re.IGNORECASE,
)

IG_HDRS = {
    "x-ig-app-id": "936619743392459",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
}

IG_EVENT_KW = re.compile(
    r"\b(fiesta|party|evento|dj|techno|house|electroni|ticket|entrada|club|boliche|"
    r"lineup|presenta|pres\.|open to close|festival|rave|arena|showcase|after)\b",
    re.IGNORECASE,
)

# Date patterns to extract from IG captions
DATE_PATTERNS = [
    # "Sábado 21 de junio", "viernes 20 de Julio"
    re.compile(r"(?:lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)"
               r"\s+(\d{1,2})\s+de\s+"
               r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
               re.IGNORECASE),
    # "Sep 12", "Sept 12", "September 12"
    re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|"
               r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
               r"\.?\s+(\d{1,2})\b", re.IGNORECASE),
    # "12/09", "12-09-2026"
    re.compile(r"\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?\b"),
]

MONTH_MAP = {
    "enero":1,"january":1,"jan":1,
    "febrero":2,"february":2,"feb":2,
    "marzo":3,"march":3,"mar":3,
    "abril":4,"april":4,"apr":4,
    "mayo":5,"may":5,
    "junio":6,"june":6,"jun":6,
    "julio":7,"july":7,"jul":7,
    "agosto":8,"august":8,"aug":8,
    "septiembre":9,"september":9,"sep":9,"sept":9,
    "octubre":10,"october":10,"oct":10,
    "noviembre":11,"november":11,"nov":11,
    "diciembre":12,"december":12,"dec":12,
}

# Events with these strings in the name are junk (scraper noise)
JUNK_NAMES = {"Gabber", "Islamic Dance", "Capybara", "TechnoViking", "WHAAAAT",
               "Russian Kid", "Suit Guy", "SIN VENTA", "Gabber Defqon",
               "WHAAAAT Rave", "Capybara Techno", "Atmosphere pres. Lucas Batcher"}

# Big venues get priority slot 1
BIG_VENUES = {"movistar arena", "mandarine", "crobar", "palacio alsina", "la biblioteca",
               "teatro vorterix", "avant garten", "under club", "club araoz"}

# Post 4-5 times per day on weekends, 2-3 on weekdays
WEEKEND_SLOTS = ["10:00", "13:00", "16:00", "19:00", "22:00"]
WEEKDAY_SLOTS = ["12:00", "18:00", "21:00"]

DRIVE_FOLDER = os.environ.get("DRIVE_FOLDER_ID", "root")


# ── Image generation ─────────────────────────────────────────────────────────

def _font(size: int):
    for path in ["/System/Library/Fonts/Supplemental/Arial Black.ttf",
                 "/System/Library/Fonts/Supplemental/Impact.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def generate_event_image(event: dict) -> Path | None:
    """Download artist photo, apply branded overlay, save to .tmp/. Returns path or None."""
    img_url = event.get("image_url", "")
    artist  = (event.get("lineup") or event.get("name") or "").split(",")[0].strip()[:30]
    venue   = (event.get("venue") or "").split(",")[0].strip()[:25]
    ev_date = event.get("date", "")
    name    = event.get("name", "")[:60]

    # Safe filename
    safe = re.sub(r"[^\w]", "_", artist or name)[:40]
    out  = ROOT / ".tmp" / f"fiestas_{safe}_{ev_date}.jpg"

    W, H = 1080, 1080
    BAR = 58
    BLACK, WHITE, GOLD, GREY = (0,0,0), (255,255,255), (210,168,40), (150,150,150)

    # Download flyer image
    photo = None
    if img_url:
        try:
            r = requests.get(img_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 5000:
                photo = Image.open(io.BytesIO(r.content)).convert("RGB")
        except Exception:
            pass

    # Format date
    try:
        dt = datetime.strptime(ev_date, "%Y-%m-%d")
        months_es = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        date_str = f"{dt.day} {months_es[dt.month-1]} {dt.year}"
    except Exception:
        date_str = ev_date

    if not photo:
        return None

    # Use the original RA flyer as-is — crop to 1080x1080 square (center crop)
    ow, oh = photo.size
    scale = max(W / ow, H / oh)
    photo = photo.resize((int(ow * scale) + 1, int(oh * scale) + 1), Image.LANCZOS)
    nw, nh = photo.size
    photo = photo.crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    photo.save(str(out), quality=92)
    return out


def extract_date_from_caption(caption: str) -> str | None:
    """Try to extract an event date from an IG caption. Returns ISO date or None."""
    today = date.today()
    year  = today.year

    # Spanish "Sábado 21 de junio"
    m = re.search(
        r"(?:lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\s+(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)",
        caption, re.IGNORECASE)
    if m:
        day   = int(m.group(1))
        month = MONTH_MAP.get(m.group(2).lower(), 0)
        if month:
            d = date(year, month, day)
            if d < today:
                d = date(year + 1, month, day)
            return d.isoformat()

    # English "Jul 12" / "September 12"
    m = re.search(
        r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"
        r"january|february|march|april|june|july|august|september|october|november|december)"
        r"\.?\s+(\d{1,2})\b", caption, re.IGNORECASE)
    if m:
        month = MONTH_MAP.get(m.group(1).lower().rstrip("t"), 0)
        day   = int(m.group(2))
        if month:
            d = date(year, month, day)
            if d < today:
                d = date(year + 1, month, day)
            return d.isoformat()

    return None


def scrape_ig_viral(handle: str, limit: int = 15) -> list[dict]:
    """Pull recent reels/posts from a viral culture account — no event date required."""
    try:
        data = ig_fetch.fetch_user(handle, limit)
    except ig_fetch.IGFetchError as e:
        print(f"  @{handle}: fetch failed — {e}")
        return []

    edges = data.get("edge_owner_to_timeline_media", {}).get("edges", [])[:limit]
    posts = []
    today = date.today()

    for edge in edges:
        n = edge["node"]
        caption = ""
        ce = n.get("edge_media_to_caption", {}).get("edges")
        if ce:
            caption = ce[0].get("node", {}).get("text", "")

        if not caption or not VIRAL_KW.search(caption):
            continue

        is_video = n.get("is_video", False)
        img_url = n.get("display_url", "")
        for r in n.get("thumbnail_resources", []):
            if r.get("config_width", 0) >= 640:
                img_url = r["src"]
                break

        shortcode = n.get("shortcode", "")
        hook = caption.split("\n")[0].strip()[:100]

        posts.append({
            "source":    f"IG @{handle} ({'reel' if is_video else 'post'})",
            "name":      shortcode,  # use shortcode as dedup key
            "date":      today.isoformat(),  # post today
            "caption":   caption[:800],
            "hook":      hook,
            "image_url": img_url,
            "post_url":  f"https://www.instagram.com/p/{shortcode}/",
            "viral":     True,
        })

    print(f"  @{handle}: {len(posts)} viral posts de {len(edges)} posts")
    return posts


def scrape_ig_source(handle: str, limit: int = 12) -> list[dict]:
    """Pull recent posts from a public IG account and return event-like ones."""
    try:
        data = ig_fetch.fetch_user(handle, limit)
    except ig_fetch.IGFetchError as e:
        print(f"  @{handle}: fetch failed — {e}")
        return []

    edges = data.get("edge_owner_to_timeline_media", {}).get("edges", [])[:limit]
    events = []
    today  = date.today()

    for edge in edges:
        n       = edge["node"]
        caption = ""
        ce      = n.get("edge_media_to_caption", {}).get("edges")
        if ce:
            caption = ce[0].get("node", {}).get("text", "")

        if not IG_EVENT_KW.search(caption):
            continue

        img_url  = n.get("display_url", "")
        # prefer higher-res thumbnail
        for r in n.get("thumbnail_resources", []):
            if r.get("config_width", 0) >= 640:
                img_url = r["src"]
                break

        ts       = n.get("taken_at_timestamp", 0)
        post_date = date.fromtimestamp(ts) if ts else today
        ev_date  = extract_date_from_caption(caption) or post_date.isoformat()

        # Skip if event date already passed
        try:
            if date.fromisoformat(ev_date) < today:
                continue
        except ValueError:
            pass

        shortcode = n.get("shortcode", "")
        events.append({
            "source":    f"@{handle}",
            "name":      caption[:80].split("\n")[0].strip(),
            "date":      ev_date,
            "venue":     "",
            "lineup":    caption[:40],
            "caption":   caption,
            "image_url": img_url,
            "post_url":  f"https://www.instagram.com/p/{shortcode}/",
        })

    print(f"  @{handle}: {len(events)} eventos de {len(edges)} posts")
    return events


def upload_image(drive, path: Path) -> str:
    from googleapiclient.http import MediaFileUpload
    f = drive.files().create(
        body={"name": path.name, "parents": [DRIVE_FOLDER]},
        media_body=MediaFileUpload(str(path), mimetype="image/jpeg"),
        fields="id",
    ).execute()
    fid = f["id"]
    drive.permissions().create(fileId=fid, body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?export=download&id={fid}"


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--ra-only",  action="store_true")
    parser.add_argument("--days-ahead", type=int, default=21)
    args = parser.parse_args()

    sheets, drive = get_services()
    today  = date.today()
    cutoff = today + timedelta(days=args.days_ahead)

    # Load already-queued captions to avoid dups
    existing = sheets.spreadsheets().values().get(
        spreadsheetId=UNIFIED_SHEET, range="'Fiestas'!B2:B500"
    ).execute().get("values", [])
    existing_caps = {r[0][:40] for r in existing if r}

    # Captions get re-worded every run, so caption matching alone re-queues
    # old events (2026-07-06: Deborah De Luca announced 3x). Also dedup by
    # event NAME against the Queue sheet ledger, any status.
    queue_names = sheets.spreadsheets().values().get(
        spreadsheetId=QUEUE_SHEET, range="Queue!C2:C500"
    ).execute().get("values", [])
    unified_names = sheets.spreadsheets().values().get(
        spreadsheetId=UNIFIED_SHEET, range="'Fiestas'!F2:F500"
    ).execute().get("values", [])
    existing_names = {r[0].strip()[:40].lower()
                      for rows_ in (queue_names, unified_names) for r in rows_
                      if r and r[0].strip()}

    seen: set[str] = set()
    by_date: dict[str, list] = defaultdict(list)

    def add_event(ev: dict):
        ev_date = ev.get("date", "")
        name    = ev.get("name", "")
        caption = ev.get("caption", "")
        img_url = ev.get("image_url", "")
        venue   = ev.get("venue", "")

        if not ev_date or not caption or not img_url:
            return
        try:
            d = date.fromisoformat(ev_date)
        except ValueError:
            return
        if d < today or d > cutoff:
            return
        if any(j.lower() in name.lower() for j in JUNK_NAMES):
            return
        key = name[:40]
        if key in seen or caption[:40] in existing_caps or key.strip().lower() in existing_names:
            return
        seen.add(key)

        priority = any(bv in venue.lower() for bv in BIG_VENUES)
        by_date[ev_date].append({**ev, "priority": priority})

    # ── Source 1: RA queue sheet ─────────────────────────────────────────────
    print("Scraping RA queue sheet…")
    queue_rows = sheets.spreadsheets().values().get(
        spreadsheetId=QUEUE_SHEET, range="Queue!A2:K500"
    ).execute().get("values", [])

    def gq(r, i): return r[i].strip() if i < len(r) else ""

    for r in queue_rows:
        m = re.search(r"ra\.co/events/(\d+)", gq(r, 10))
        add_event({
            "source":    "RA",
            "name":      gq(r, 2),
            "date":      gq(r, 3),
            "venue":     gq(r, 4),
            "lineup":    gq(r, 6),
            "caption":   gq(r, 7),
            "image_url": gq(r, 9),
            "ra_id":     m.group(1) if m else "",
        })
    print(f"  RA: {sum(len(v) for v in by_date.values())} eventos únicos hasta ahora")

    # ── Source 2: IG event accounts ─────────────────────────────────────────
    if not args.ra_only:
        print("\nScraping cuentas IG…")
        for handle in IG_SOURCES:
            for ev in scrape_ig_source(handle):
                if not ev.get("caption"):
                    continue
                lines = ev["caption"].split("\n")
                ev["name"]    = re.sub(r"[🔥🎵🎶💥✨🌟⚡]", "", lines[0]).strip()[:70]
                ev["caption"] = ev["caption"][:800]
                add_event(ev)
            time.sleep(1.5)

    # ── Source 3: IG viral culture accounts ─────────────────────────────────
    viral_rows = []
    if not args.ra_only:
        print("\nScraping cuentas virales…")
        for handle in IG_VIRAL_SOURCES:
            for post in scrape_ig_viral(handle):
                shortcode = post["name"]  # used as dedup key
                if shortcode in existing_names or shortcode in seen:
                    continue
                if not post.get("image_url"):
                    continue
                seen.add(shortcode)
                hook = post.get("hook", post["caption"].split("\n")[0])[:100]
                viral_rows.append([
                    datetime.now(AR_TZ).strftime("%Y-%m-%d %H:%M"),
                    post["source"],
                    shortcode,
                    date.today().isoformat(),
                    "",  # venue
                    "",  # city
                    "",  # lineup
                    post["caption"][:800],
                    hook,
                    post["image_url"],
                    post["post_url"],
                    "approved",
                ])
                print(f"  [viral] {hook[:60]}")
            time.sleep(1.5)

    if not by_date and not viral_rows:
        print("Nothing new to queue.")
        return

    # Sort each day: priority first, then alphabetical
    new_rows = []
    alt_counter = 0  # feed mix: alternate official flyer / our own branded card
    for ev_date in sorted(by_date):
        d       = date.fromisoformat(ev_date)
        is_wknd = d.weekday() in (4, 5, 6)
        slots   = WEEKEND_SLOTS if is_wknd else WEEKDAY_SLOTS
        events  = sorted(by_date[ev_date], key=lambda e: (not e["priority"], e["name"]))[:len(slots)]

        for idx, ev in enumerate(events):
            slot = slots[idx]
            img_url = ev["image_url"]

            alt_counter += 1
            if alt_counter % 2 == 0 and not args.dry_run:
                try:
                    from tools.fiestas_card import make_card, ra_artist_photo
                    # prefer the DJ's public profile photo; fall back to the flyer
                    photo = ra_artist_photo(ev["ra_id"]) if ev.get("ra_id") else None
                    if not photo:
                        photo = requests.get(img_url, timeout=15,
                                             headers={"User-Agent": "Mozilla/5.0"}).content
                    card = make_card({"name": ev["name"], "date": ev_date,
                                      "venue": ev.get("venue", ""),
                                      "lineup": ev.get("lineup", "")}, photo)
                    img_url = upload_image(drive, card)
                    print(f"  [card propia] {ev['name'][:40]}")
                except Exception as e:
                    print(f"  card propia falló ({str(e)[:60]}), uso flyer oficial")

            row = [
                datetime.now(AR_TZ).strftime("%Y-%m-%d %H:%M"),
                ev["caption"],
                img_url,
                f"{ev_date} {slot}",
                "approved",
                ev["name"][:50],
                "",
            ]
            new_rows.append(row)
            tag = "BIG" if ev["priority"] else "   "
            print(f"  [{tag}] {ev_date} {slot} — {ev['name'][:50]}")

    if not args.dry_run and new_rows:
        sheets.spreadsheets().values().append(
            spreadsheetId=UNIFIED_SHEET,
            range="'Fiestas'!A1",
            valueInputOption="RAW",
            body={"values": new_rows},
        ).execute()
        print(f"\n{len(new_rows)} eventos aprobados y listos para publicar.")
    elif args.dry_run:
        print(f"\n[DRY RUN] {len(new_rows)} eventos a encolar.")

    # Write viral content to Fiestas Queue sheet
    if not args.dry_run and viral_rows:
        sheets.spreadsheets().values().append(
            spreadsheetId=QUEUE_SHEET,
            range="Queue!A1",
            valueInputOption="RAW",
            body={"values": viral_rows},
        ).execute()
        print(f"{len(viral_rows)} posts virales agregados a la cola.")
    elif args.dry_run and viral_rows:
        print(f"[DRY RUN] {len(viral_rows)} posts virales a encolar.")


if __name__ == "__main__":
    main()
