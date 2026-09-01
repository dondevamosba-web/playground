#!/usr/bin/env python3
"""
Publish the single most urgent approved Fiestas post (nearest Event Date).
Same posting logic as publish_approved_events.py, but only touches one row
per run instead of publishing every approved row at once.

Usage:
  python3 tools/publish_fiestas_next.py
  python3 tools/publish_fiestas_next.py --dry-run
  python3 tools/publish_fiestas_next.py --feed-only
  python3 tools/publish_fiestas_next.py --story-only
"""

import argparse
import os
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.publish_approved_events import (
    get_approved_rows, update_row, post_to_instagram, col,
    COL_EVENT_NAME, COL_EVENT_DATE, COL_SOURCE, COL_FEED_CAPTION,
    COL_STORY_CAPTION, COL_IMAGE_URL, SHEET_ID_ENV,
)

AR_TZ = timezone(timedelta(hours=-3))


def parse_event_date(raw: str):
    raw = (raw or "").strip()[:10]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None  # undated content (e.g. viral reposts) sorts last


def pick_next(approved: list[tuple[int, list]]):
    today = datetime.now(AR_TZ).date()

    def sort_key(item):
        _, row = item
        d = parse_event_date(col(row, COL_EVENT_DATE))
        if d is None:
            return (2, date.max)          # no date: lowest priority
        if d < today:
            return (1, d)                 # past event: still queued, low priority
        return (0, d)                     # upcoming: prioritize by soonest

    return sorted(approved, key=sort_key)[0] if approved else None


def main():
    parser = argparse.ArgumentParser(description="Publish the next most urgent approved Fiestas post")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--feed-only", action="store_true")
    parser.add_argument("--story-only", action="store_true")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ID_ENV, "").strip()
    if not sheet_id:
        print(f"ERROR: {SHEET_ID_ENV} not set in .env")
        sys.exit(1)

    sheets_svc, _ = get_services()
    approved = get_approved_rows(sheets_svc, sheet_id)

    if not approved:
        print("No approved posts to publish.")
        return

    row_idx, row = pick_next(approved)
    name      = col(row, COL_EVENT_NAME)
    event_date = col(row, COL_EVENT_DATE)
    feed_cap  = col(row, COL_FEED_CAPTION)
    story_cap = col(row, COL_STORY_CAPTION)
    image_url = col(row, COL_IMAGE_URL)
    source    = col(row, COL_SOURCE)
    is_reel   = "reel" in source.lower()
    feed_type = "reel" if is_reel else "single"

    print(f"Publishing most urgent approved post ({len(approved)} approved total): {name} — {event_date}")

    post_ids = []

    if not args.story_only:
        if feed_cap and image_url:
            print(f"  → Feed post ({feed_type})...")
            pid = post_to_instagram(feed_type, feed_cap, image_url, args.dry_run, is_video=is_reel)
            if pid:
                post_ids.append(f"feed:{pid}")
        else:
            print("  SKIP feed — missing caption or image URL")

    if not args.feed_only:
        story_text = story_cap or name
        if image_url:
            print("  → Story...")
            pid = post_to_instagram("story", story_text, image_url, args.dry_run)
            if pid:
                post_ids.append(f"story:{pid}")
        else:
            print("  SKIP story — no image URL")

    if args.dry_run:
        print("\n[DRY RUN] Sheet not updated.")
        return

    combined_id = " | ".join(post_ids) if post_ids else "error"
    status = "posted" if post_ids else "error"
    update_row(sheets_svc, sheet_id, row_idx, status, combined_id)
    print(f"\nSheet updated: {status}")
    print(f"post_id: {combined_id}")


if __name__ == "__main__":
    main()
