#!/usr/bin/env python3
"""
Read the Fiestas approval sheet and publish any rows marked Status="approved".
Posts feed image + story to Instagram. Updates Status → "posted" and records Post ID.

Usage:
  python3 tools/publish_approved_events.py              # publish all approved rows
  python3 tools/publish_approved_events.py --dry-run   # show what would be posted
  python3 tools/publish_approved_events.py --feed-only  # skip stories
  python3 tools/publish_approved_events.py --story-only # skip feed posts
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

SHEET_ID_ENV = "FIESTAS_APPROVAL_SHEET_ID"
AR_TZ = timezone(timedelta(hours=-3))

# Column indices (0-based), must match queue_event_posts.py HEADERS
COL_QUEUED_AT     = 0
COL_SOURCE        = 1
COL_EVENT_NAME    = 2
COL_EVENT_DATE    = 3
COL_VENUE         = 4
COL_CITY          = 5
COL_LINEUP        = 6
COL_FEED_CAPTION  = 7
COL_STORY_CAPTION = 8
COL_IMAGE_URL     = 9
COL_SOURCE_URL    = 10
COL_STATUS        = 11
COL_POST_ID       = 12
COL_NOTES         = 13


def col(row: list, idx: int, default: str = "") -> str:
    return row[idx].strip() if idx < len(row) else default


def get_approved_rows(sheets, sheet_id: str) -> list[tuple[int, list]]:
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Queue!A:N",
    ).execute()
    rows = resp.get("values", [])

    approved = []
    for i, row in enumerate(rows[1:], start=1):  # skip header, i is 0-based data index
        if col(row, COL_STATUS).lower() == "approved":
            approved.append((i, row))
    return approved


def update_row(sheets, sheet_id: str, row_idx: int, status: str, post_id: str):
    # row_idx is 0-based data row → sheet row = row_idx + 2 (header + 1-based)
    sheet_row = row_idx + 2
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"Queue!L{sheet_row}:M{sheet_row}",
        valueInputOption="RAW",
        body={"values": [[status, post_id]]},
    ).execute()


def post_to_instagram(post_type: str, caption: str, media_url: str, dry_run: bool, is_video: bool = False) -> str | None:
    if not media_url:
        return None

    # Detect if the media is a video based on URL or post_type hint
    video_exts = (".mp4", ".mov")
    url_is_video = any(e in media_url.lower() for e in video_exts) or is_video

    cmd = [
        "python3", str(ROOT / "tools" / "post_instagram.py"),
        "--account", "fiestas",
        "--type", post_type,
        "--caption", caption,
        "--skip-facebook",
    ]

    if url_is_video:
        cmd += ["--video-url", media_url]
    else:
        cmd += ["--image-url", media_url]

    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = result.stdout.strip()
    if output:
        print(f"      {output[:300]}")

    if result.returncode != 0:
        print(f"      ERROR: {result.stderr.strip()[:300]}")
        return None

    for line in output.splitlines():
        for kw in ("Media ID:", "post ID:", "carousel ID:"):
            if kw in line:
                return line.split(":")[-1].strip().split()[0]
    return "posted"


def main():
    parser = argparse.ArgumentParser(description="Publish approved Fiestas posts to Instagram")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--feed-only", action="store_true", help="Skip stories")
    parser.add_argument("--story-only", action="store_true", help="Skip feed posts")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ID_ENV, "").strip()
    if not sheet_id:
        print(f"ERROR: {SHEET_ID_ENV} not set in .env")
        print("Run queue_event_posts.py first to create the sheet, then set the ID.")
        sys.exit(1)

    sheets_svc, _ = get_services()
    approved = get_approved_rows(sheets_svc, sheet_id)

    if not approved:
        print("No approved posts to publish.")
        return

    print(f"Found {len(approved)} approved post(s).")

    for row_idx, row in approved:
        name        = col(row, COL_EVENT_NAME)
        feed_cap    = col(row, COL_FEED_CAPTION)
        story_cap   = col(row, COL_STORY_CAPTION)
        image_url   = col(row, COL_IMAGE_URL)

        print(f"\n  Publishing: {name}")

        post_ids = []

        # Detect if this is a video/reel repost (Source column contains "reel")
        source  = col(row, COL_SOURCE)
        is_reel = "reel" in source.lower()
        feed_type = "reel" if is_reel else "single"

        # Feed post
        if not args.story_only:
            if feed_cap and image_url:
                print(f"    → Feed post ({feed_type})...")
                pid = post_to_instagram(feed_type, feed_cap, image_url, args.dry_run, is_video=is_reel)
                if pid:
                    post_ids.append(f"feed:{pid}")
            else:
                print("    SKIP feed — missing caption or image URL")

        # Story post
        if not args.feed_only:
            story_text = story_cap or name
            if image_url:
                print("    → Story...")
                # Stories don't support text overlay via API — post image, caption is metadata only
                pid = post_to_instagram("story", story_text, image_url, args.dry_run)
                if pid:
                    post_ids.append(f"story:{pid}")
            else:
                print("    SKIP story — no image URL")

        if not args.dry_run:
            combined_id = " | ".join(post_ids) if post_ids else "error"
            status = "posted" if post_ids else "error"
            update_row(sheets_svc, sheet_id, row_idx, status, combined_id)
            print(f"    Sheet updated: {status}")

    print("\nDone.")


if __name__ == "__main__":
    main()
