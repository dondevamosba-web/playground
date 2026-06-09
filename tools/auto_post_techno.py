#!/usr/bin/env python3
"""
Read the Techno content calendar (Google Sheet) and publish any pending posts that are due.
Updates each row's Status → "posted" and records the Post ID.

Usage:
  python3 tools/auto_post_techno.py            # post all due pending items
  python3 tools/auto_post_techno.py --dry-run  # show what would be posted
  python3 tools/auto_post_techno.py --force    # post all pending regardless of time
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"
AR_TZ = timezone(timedelta(hours=-3))

COL_DATE      = 0
COL_TIME      = 1
COL_PRODUCT   = 3
COL_BRAND     = 4
COL_POST_TYPE = 5
COL_CAPTION   = 6
COL_HASHTAGS  = 7
COL_MEDIA_URL = 8
COL_STATUS    = 9
COL_POST_ID   = 10


def col(row, idx, default=""):
    return row[idx].strip() if idx < len(row) else default


def parse_dt(date_str, time_str):
    naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return naive.replace(tzinfo=AR_TZ)


def publish(row, dry_run):
    post_type = col(row, COL_POST_TYPE) or "single"
    caption   = col(row, COL_CAPTION)
    media_url = col(row, COL_MEDIA_URL)
    hashtags  = col(row, COL_HASHTAGS)

    if not media_url:
        print("    SKIP — no Media URL set in sheet")
        return None

    env = os.environ.copy()
    env["FACEBOOK_PAGE_ID"]                 = os.getenv("TECHNO_FACEBOOK_PAGE_ID", "")
    env["INSTAGRAM_BUSINESS_ACCOUNT_ID"]    = os.getenv("TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    cmd = [
        "python3", str(ROOT / "tools" / "post_instagram.py"),
        "--account", "techno",
        "--type", post_type if post_type in ("reel", "carousel") else "single",
        "--caption", caption,
    ]
    if hashtags:
        cmd += ["--hashtags"] + hashtags.split()
    if post_type == "reel":
        cmd += ["--video-url", media_url]
    else:
        cmd += ["--image-url", media_url]
    if dry_run:
        cmd += ["--dry-run"]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr.strip()}")
        return None

    output = result.stdout.strip()
    print(f"    {output[:200]}")

    for line in output.splitlines():
        for keyword in ("Media ID:", "post ID:", "reel ID:"):
            if keyword in line:
                return line.split(":")[-1].strip().split()[0]
    return "posted"


def update_status(sheets, sheet_id, row_idx, status, post_id):
    range_str = f"J{row_idx + 2}:K{row_idx + 2}"
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_str,
        valueInputOption="RAW",
        body={"values": [[status, post_id]]},
    ).execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force",   action="store_true")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ENV_KEY)
    if not sheet_id:
        print(f"ERROR: {SHEET_ENV_KEY} not set in .env")
        print("Run: python3 tools/fill_content_techno.py")
        sys.exit(1)

    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:K1000"
    ).execute().get("values", [])

    now = datetime.now(tz=AR_TZ)
    print(f"[Techno] Checking calendar — {now.strftime('%Y-%m-%d %H:%M')} AR time")

    due = [
        (i, row, parse_dt(col(row, COL_DATE), col(row, COL_TIME)))
        for i, row in enumerate(rows)
        if col(row, COL_STATUS) == "pending"
        and col(row, COL_DATE)
        and col(row, COL_TIME)
        and col(row, COL_MEDIA_URL)
        and (args.force or parse_dt(col(row, COL_DATE), col(row, COL_TIME)) <= now)
    ]

    if not due:
        print("Nothing due right now.")
        return

    print(f"{len(due)} post(s) to publish:\n")
    posted = 0
    for i, row, post_dt in due:
        product = col(row, COL_PRODUCT)
        brand   = col(row, COL_BRAND)
        media   = col(row, COL_MEDIA_URL)
        print(f"  [{post_dt.strftime('%Y-%m-%d %H:%M')}] {brand.upper()} — {product}")
        print(f"  Media: {media[:60]}")

        post_id = publish(row, args.dry_run)

        if not args.dry_run and post_id:
            update_status(sheets, sheet_id, i, "posted", post_id)
            print(f"    Sheet updated → posted (ID: {post_id})")
            posted += 1
        print()

    print(f"Done. {posted}/{len(due)} published.")


if __name__ == "__main__":
    main()
