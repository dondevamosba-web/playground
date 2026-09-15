#!/usr/bin/env python3
"""
Publish the single most urgent approved Fiestas post as a story, then stop.

Built to be called on a timer (every 60 min). Unlike feed posts, stories are
ephemeral and high-velocity — good for retargeting and top-of-feed awareness.

Stories include the event image + interactive stickers:
- Countdown to event date
- Poll: "Vas a ir?"
- Swipe-up link to tickets (if 10K+ followers)

Usage:
  python3 tools/publish_fiestas_stories.py --dry-run
  python3 tools/publish_fiestas_stories.py
  python3 tools/publish_fiestas_stories.py --only-flyers
"""
import argparse
import os
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

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))
COL_SOURCE, COL_NAME, COL_DATE, COL_CAPTION = 1, 2, 3, 7
COL_IMAGE, COL_STATUS, COL_POST_ID, COL_NOTES = 9, 11, 12, 13


def cell(row, idx):
    return (row[idx] or "").strip() if idx < len(row) else ""


def publish_story(ig_id, token, image_url, caption):
    """Publish image to stories. No video/reel support yet."""
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }

    res = requests.post(f"{GRAPH}/{ig_id}/media", data=payload, timeout=60).json()
    if "id" not in res:
        print(f"  ERROR container: {res}")
        return None

    # Stories publish immediately (no FINISHED check needed)
    time.sleep(1)
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
        # Stories: image only (no videos)
        if not cell(r, COL_IMAGE):
            continue
        candidates.append((when or "9999-12-31", i + 2, r))

    if not candidates:
        print(f"[{stamp}] Nada aprobado para story.")
        return 0

    candidates.sort(key=lambda c: (c[0], c[1]))
    when, sheet_row, r = candidates[0]
    name = cell(r, COL_NAME)
    print(f"[{stamp}] {len(candidates)} en cola. Story fila {sheet_row}: {name} ({when})")

    if args.dry_run:
        print("  [dry-run] no se publicó nada")
        return 0

    media_id = publish_story(ig_id, token, cell(r, COL_IMAGE), cell(r, COL_CAPTION))
    if not media_id:
        return 1

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": [
            {"range": f"Queue!L{sheet_row}", "values": [["posted"]]},
            {"range": f"Queue!M{sheet_row}", "values": [[media_id]]},
        ]}).execute()
    print(f"  OK {media_id} — quedan {len(candidates) - 1}")

    # Add interactive stickers to story
    event_date = cell(r, COL_DATE)
    try:
        subprocess.run(
            [sys.executable, "tools/story_stickers.py",
             "--event-date", event_date, "--apply"],
            capture_output=True, timeout=30, cwd=ROOT)
        print(f"  ✓ Story stickers configured")
    except Exception as e:
        print(f"  Story stickers error: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
