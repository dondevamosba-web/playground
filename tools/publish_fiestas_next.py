#!/usr/bin/env python3
"""
Publish the single most urgent approved Fiestas post, then stop.

Built to be called on a timer. Unlike run_fiestas() in publish_one_each.py, which
takes whichever approved row appears first in the sheet, this picks the row whose
**event date is soonest**, so a party four days away goes out before one in November.

Publishes to the feed only — no story — and marks the row posted.

Usage:
  python3 tools/publish_fiestas_next.py --dry-run
  python3 tools/publish_fiestas_next.py
  python3 tools/publish_fiestas_next.py --only-flyers
"""
import argparse
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services
from tools.monetize_pipeline import MonetizationConfig
from tools.notify_discord import notify

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))
COL_SOURCE, COL_NAME, COL_DATE, COL_CAPTION = 1, 2, 3, 7
COL_IMAGE, COL_STATUS, COL_POST_ID, COL_NOTES = 9, 11, 12, 13


def cell(row, idx):
    return (row[idx] or "").strip() if idx < len(row) else ""


def check_dedup(event_name, event_date):
    """Check if event already queued in other accounts."""
    try:
        result = subprocess.run(
            [sys.executable, "tools/cross_account_dedup.py",
             "--event", event_name, "--date", event_date, "--account", "fiestas"],
            capture_output=True, timeout=30, cwd=ROOT)
        return result.returncode == 0
    except Exception as e:
        print(f"  Dedup check error: {e}")
        return True


def add_ticket_links(caption):
    """Extract and add ticket links to caption if missing."""
    if not caption or "Entradas:" in caption or "entradas:" in caption:
        return caption

    patterns = [
        r"https?://[a-z0-9.-]*ticketmaster[a-z0-9.-]*/[^\s]+",
        r"https?://[a-z0-9.-]*eventbrite[a-z0-9.-]*/[^\s]+",
        r"https?://bit\.ly/[a-zA-Z0-9]+",
    ]

    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            url = match.group(0)
            caption = f"{caption}\n\nEntradas: {url}"
            print(f"  ✓ Added ticket link")
            break
    return caption


def add_email_cta(caption, event_name):
    """Add email subscription CTA based on event importance."""
    if not caption or "📧" in caption or "Suscrib" in caption:
        return caption

    # Only add to high-value events
    high_value_keywords = ["creamfields", "solomun", "digweed", "charlotte", "hardwell"]
    if not any(kw in event_name.lower() for kw in high_value_keywords):
        return caption

    linktree = os.environ.get("FIESTAS_LINKTREE", "")
    if linktree:
        caption = f"{caption}\n\n📧 Eventos exclusivos en bio"
        print(f"  ✓ Added email CTA")

    return caption


def publish(ig_id, token, caption, image_url, video_url):
    if video_url:
        payload = {"media_type": "REELS", "video_url": video_url,
                   "caption": caption, "access_token": token}
    else:
        payload = {"image_url": image_url, "caption": caption, "access_token": token}

    res = requests.post(f"{GRAPH}/{ig_id}/media", data=payload, timeout=60).json()
    if "id" not in res:
        print(f"  ERROR container: {res}")
        return None

    if video_url:  # reels need server-side processing before publish
        for _ in range(24):
            st = requests.get(f"{GRAPH}/{res['id']}",
                              params={"fields": "status_code", "access_token": token},
                              timeout=30).json()
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                print(f"  ERROR procesando reel: {st}")
                return None
            time.sleep(5)

    time.sleep(2)
    res2 = requests.post(f"{GRAPH}/{ig_id}/media_publish",
                         data={"creation_id": res["id"], "access_token": token},
                         timeout=60).json()
    if "id" not in res2:
        print(f"  ERROR publish: {res2}")
        return None
    return res2["id"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--only-flyers", action="store_true",
                   help="Ignore rows whose Source column is not a flyer")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    ig_id = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    today = date.today().isoformat()
    stamp = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d %H:%M")

    candidates = []
    for i, r in enumerate(rows):
        if cell(r, COL_STATUS) != "approved" or cell(r, COL_POST_ID):
            continue
        when = cell(r, COL_DATE)
        if when and when < today:
            continue
        if args.only_flyers and "(flyer)" not in cell(r, COL_SOURCE):
            continue
        if not cell(r, COL_CAPTION):
            continue
        notes = cell(r, COL_NOTES)
        video = notes[6:].strip() if notes.startswith("VIDEO:") else ""
        if not cell(r, COL_IMAGE) and not video:
            continue
        candidates.append((when or "9999-12-31", i + 2, r, video))

    if not candidates:
        print(f"[{stamp}] Nada aprobado para publicar.")
        return 0

    candidates.sort(key=lambda c: (c[0], c[1]))
    when, sheet_row, r, video = candidates[0]
    name = cell(r, COL_NAME)
    print(f"[{stamp}] {len(candidates)} en cola. Publicando fila {sheet_row}: "
          f"{name} ({when})")

    # Check for duplicates in other accounts
    if not check_dedup(name, when):
        print(f"  ⚠️  DUPLICATE found in other account. Skipping.")
        return 1

    # Add ticket links if available
    caption = cell(r, COL_CAPTION)
    caption = add_ticket_links(caption)
    caption = add_email_cta(caption, name)

    if args.dry_run:
        print("  [dry-run] no se publicó nada")
        notify(account="fiestas", caption=caption, image_url=cell(r, COL_IMAGE), status="dry-run")
        return 0

    # Log monetization opportunity
    monetizer = MonetizationConfig()
    decisions = monetizer.should_monetize(name)
    if decisions["email_cta"]:
        monetizer.log_revenue_event("email", name, 0.0, "linktree_click")

    media_id = publish(ig_id, token, caption, cell(r, COL_IMAGE), video)
    if not media_id:
        notify(account="fiestas", caption=caption, image_url=cell(r, COL_IMAGE), status="error")
        return 1

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": [
            {"range": f"Queue!L{sheet_row}", "values": [["posted"]]},
            {"range": f"Queue!M{sheet_row}", "values": [[media_id]]},
        ]}).execute()
    print(f"  OK {media_id} — quedan {len(candidates) - 1}")
    notify(account="fiestas", caption=caption, image_url=cell(r, COL_IMAGE), status="posted", post_id=media_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
