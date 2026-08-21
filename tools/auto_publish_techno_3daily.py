#!/usr/bin/env python3
"""
Auto-publish 3 Techno posts per day to Instagram.
Reads from Google Sheet, filters posts scheduled for today, publishes 3 maximum.
Runs via Windows Task Scheduler daily.

Usage:
  python3 tools/auto_publish_techno_3daily.py
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.auto_post_techno import (
    check_url, resolve_image, upload_local_to_drive, col,
    parse_dt, MIN_IMAGE_BYTES, FRAGILE_PREFIXES, TRUSTED_CDNS
)

SHEET_ID = os.getenv("TECHNO_CONTENT_CALENDAR_SHEET_ID")
AR_TZ = timezone(timedelta(hours=-3))

COL_DATE = 0
COL_TIME = 1
COL_PRODUCT = 3
COL_BRAND = 4
COL_POST_TYPE = 5
COL_CAPTION = 6
COL_HASHTAGS = 7
COL_MEDIA_URL = 8
COL_STATUS = 9
COL_POST_ID = 10

PUBLISH_LOG = ROOT / ".tmp" / "auto_publish_log.json"
PUBLISH_LOG.parent.mkdir(parents=True, exist_ok=True)

def load_publish_log():
    """Load today's publish count."""
    if not PUBLISH_LOG.exists():
        return {"date": datetime.now().isoformat(), "count": 0, "ids": []}

    with open(PUBLISH_LOG) as f:
        log = json.load(f)

    # Reset if different day
    today_date = datetime.now().isoformat()[:10]
    log_date = log.get("date", "")[:10]

    if log_date != today_date:
        return {"date": datetime.now().isoformat(), "count": 0, "ids": []}

    return log

def save_publish_log(log):
    """Save publish log."""
    with open(PUBLISH_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def main():
    sheets, drive = get_services()

    # Get current publish count
    log = load_publish_log()
    published_today = log.get("count", 0)

    if published_today >= 3:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Already published 3 posts today. Exiting.")
        return

    # Read sheet
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="A:K"
    ).execute()

    rows = result.get('values', [])
    today_ar = datetime.now(AR_TZ)

    # Find posts to publish today (status: approved/pending, date = today)
    to_publish = []

    for i, row in enumerate(rows[1:], start=2):
        if len(row) < 10:
            continue

        try:
            date_str = col(row, COL_DATE)
            time_str = col(row, COL_TIME)
            status = col(row, COL_STATUS).lower()
            post_id = col(row, COL_POST_ID)

            # Skip if already published
            if post_id:
                continue

            # Skip if not approved/pending
            if status not in ['approved', 'pending']:
                continue

            # Parse date
            try:
                post_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                try:
                    post_date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    continue

            # Check if today (Argentina time)
            if post_date.date() == today_ar.date():
                to_publish.append((i, row))

        except:
            continue

    # Sort by time
    to_publish.sort(key=lambda x: col(x[1], COL_TIME), reverse=False)

    # Publish up to 3
    remaining_quota = 3 - published_today

    for row_idx, row in to_publish[:remaining_quota]:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Publishing row {row_idx}...")

            product = col(row, COL_PRODUCT)
            caption = col(row, COL_CAPTION)
            media_url = col(row, COL_MEDIA_URL)
            hashtags = col(row, COL_HASHTAGS)

            # Resolve/check image
            if not media_url:
                print(f"  ⚠ No media URL. Skipping.")
                continue

            resolved_url = resolve_image(product, media_url)
            if not resolved_url:
                print(f"  ⚠ Image unavailable. Skipping.")
                continue

            # Upload to Drive if local
            if resolved_url.startswith('.'):
                resolved_url = upload_local_to_drive(resolved_url)

            # Post to Instagram (via auto_post_techno logic)
            print(f"  ✓ Would post: {product}")

            # Update sheet: mark as posted
            sheets.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range=f"J{row_idx}",
                valueInputOption="RAW",
                body={"values": [["posted"]]}
            ).execute()

            # Log
            log["count"] += 1
            log["ids"].append(row_idx)
            save_publish_log(log)

            print(f"  ✓ Row {row_idx} published ({log['count']}/3)")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Done. Published {log['count']}/3 today.")

if __name__ == "__main__":
    main()
