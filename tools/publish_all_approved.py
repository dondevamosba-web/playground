#!/usr/bin/env python3
"""
Read all 4 tabs in the unified approval sheet and publish any row with Status="approved".
Supports images and reels (video URL in col H).
Updates Status → "posted" and writes Meta media ID to Post ID column.
After each successful image post, automatically publishes a matching story (--no-story to skip).

Usage:
  python3 tools/publish_all_approved.py              # all accounts
  python3 tools/publish_all_approved.py --tab Fiestas  # one account only
  python3 tools/publish_all_approved.py --dry-run    # preview without posting
  python3 tools/publish_all_approved.py --no-story   # skip story auto-post
"""

import argparse
import os
import sys
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.publish_story import publish_story_for_post

SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
TOKEN    = os.environ["INSTAGRAM_ACCESS_TOKEN"]
GRAPH    = "https://graph.facebook.com/v19.0"

ACCOUNTS = {
    "Ola Digital": os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Storm":       os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Fiestas":     os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Techno":      os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
}

# Column indices (0-based)
COL_CAPTION   = 1
COL_IMAGE_URL = 2
COL_STATUS    = 4
COL_POST_ID   = 6
COL_VIDEO_URL = 7  # reels only — video in H, thumbnail in C


def wait_for_container(container_id, max_wait=120):
    for _ in range(max_wait // 10):
        time.sleep(10)
        r = requests.get(f"{GRAPH}/{container_id}", params={
            "fields": "status_code,status",
            "access_token": TOKEN,
        })
        s = r.json()
        code = s.get("status_code", "")
        if code == "FINISHED":
            return True
        if code == "ERROR":
            print(f"    Processing error: {s}")
            return False
    return False


def publish_row(ig_id, row, dry_run):
    caption   = row[COL_CAPTION] if len(row) > COL_CAPTION else ""
    image_url = row[COL_IMAGE_URL] if len(row) > COL_IMAGE_URL else ""
    video_url = row[COL_VIDEO_URL] if len(row) > COL_VIDEO_URL else ""

    is_reel = bool(video_url.strip())

    if dry_run:
        kind = "REEL" if is_reel else "IMAGE"
        print(f"    [dry-run] Would post {kind}: {caption[:60]}...")
        return "dry-run"

    if is_reel:
        r = requests.post(f"{GRAPH}/{ig_id}/media", data={
            "media_type": "REELS",
            "video_url": video_url,
            "cover_url": image_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": TOKEN,
        })
    else:
        r = requests.post(f"{GRAPH}/{ig_id}/media", data={
            "image_url": image_url,
            "caption": caption,
            "access_token": TOKEN,
        })

    res = r.json()
    if "id" not in res:
        print(f"    ERROR creating container: {res}")
        return None

    container_id = res["id"]

    if is_reel:
        print(f"    Container {container_id} — waiting for reel processing...")
        if not wait_for_container(container_id):
            return None

    time.sleep(2)
    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish", data={
        "creation_id": container_id,
        "access_token": TOKEN,
    })
    res2 = r2.json()
    if "id" not in res2:
        print(f"    ERROR publishing: {res2}")
        return None

    return res2["id"]


MAX_PER_RUN = 2       # max posts per account per cron run — avoids bot detection
POST_DELAY  = 30      # seconds between posts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tab", help="Only publish this tab (e.g. 'Fiestas')")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-story", action="store_true", help="Skip story auto-post")
    parser.add_argument("--max", type=int, default=MAX_PER_RUN, help="Max posts per account per run")
    args = parser.parse_args()

    sheets, _ = get_services()
    tabs = [args.tab] if args.tab else list(ACCOUNTS.keys())
    total_posted = 0

    for tab in tabs:
        ig_id = ACCOUNTS.get(tab)
        if not ig_id:
            print(f"Unknown tab: {tab}")
            continue

        result = sheets.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"'{tab}'!A1:H200"
        ).execute()
        rows = result.get("values", [])

        def sched_ok(row):
            """Due per Schedule Date (col D): not future, not >24h stale.
            Slots are set ~1 day before each event, so a 24h catch-up window
            can never publish after the event (Mac offline on Jul 4 almost
            promoted finished parties with the previous 48h window).
            Rows without a parseable date keep the old publish-now behavior."""
            raw = (row[3] if len(row) > 3 else "").strip()
            try:
                sched = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(
                    tzinfo=timezone(timedelta(hours=-3)))
            except ValueError:
                return True
            now = datetime.now(timezone(timedelta(hours=-3)))
            return sched <= now and (now - sched) <= timedelta(hours=24)

        # Dedup by caption prefix against rows already posted in this tab
        # (same idea as publish_one_each's posted-name guard: a re-queued
        # event gets a caption whose first chars name the same event)
        posted_captions = {
            (row[COL_CAPTION] if len(row) > COL_CAPTION else "").strip()[:60].lower()
            for row in rows[1:]
            if len(row) > COL_POST_ID and row[COL_POST_ID].strip()
        }

        pending = [
            (i + 2, row)
            for i, row in enumerate(rows[1:])
            if len(row) > COL_STATUS
            and row[COL_STATUS].strip().lower() == "approved"
            and (len(row) <= COL_POST_ID or not row[COL_POST_ID].strip())
            and (row[COL_CAPTION] if len(row) > COL_CAPTION else "").strip()[:60].lower() not in posted_captions
            and sched_ok(row)
        ]

        if not pending:
            print(f"{tab}: nothing to publish")
            continue

        # Limit to MAX_PER_RUN per account per cron execution
        batch = pending[:args.max]
        skipped = len(pending) - len(batch)
        print(f"\n{tab} — publishing {len(batch)}/{len(pending)} (limit {args.max}/run{', '+str(skipped)+' deferred' if skipped else ''})")

        for sheet_row, row in batch:
            caption_preview = (row[COL_CAPTION] if len(row) > COL_CAPTION else "")[:60]
            print(f"  Row {sheet_row}: {caption_preview}...")

            media_id = publish_row(ig_id, row, args.dry_run)

            if media_id and media_id != "dry-run":
                sheets.spreadsheets().values().batchUpdate(
                    spreadsheetId=SHEET_ID,
                    body={"valueInputOption": "RAW", "data": [
                        {"range": f"'{tab}'!E{sheet_row}", "values": [["posted"]]},
                        {"range": f"'{tab}'!G{sheet_row}", "values": [[media_id]]},
                    ]}
                ).execute()
                print(f"    Posted — Media ID: {media_id}")
                total_posted += 1
                is_reel = bool((row[COL_VIDEO_URL] if len(row) > COL_VIDEO_URL else "").strip())
                image_url = row[COL_IMAGE_URL] if len(row) > COL_IMAGE_URL else ""
                if not is_reel and image_url and not args.no_story:
                    print(f"    Publishing story…")
                    story_id = publish_story_for_post(tab, image_url, media_id, dry_run=args.dry_run)
                    if story_id:
                        print(f"    Story — Media ID: {story_id}")
                if batch.index((sheet_row, row)) < len(batch) - 1:
                    print(f"    Waiting {POST_DELAY}s…")
                    time.sleep(POST_DELAY)

    print(f"\nDone. {total_posted} post(s) published.")


if __name__ == "__main__":
    main()
