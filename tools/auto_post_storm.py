#!/usr/bin/env python3
"""
Read the Storm Digital content calendar (Google Sheet) and publish any pending posts that are due.
Updates each row's Status → "posted" and records the Post ID.

Usage:
  python3 tools/auto_post_storm.py            # post all due pending items
  python3 tools/auto_post_storm.py --dry-run  # show what would be posted
  python3 tools/auto_post_storm.py --force    # post regardless of scheduled time
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
from tools.notify_discord import notify

SHEET_ENV_KEY = "STORM_CONTENT_CALENDAR_SHEET_ID"
AR_TZ = timezone(timedelta(hours=-3))

COL_DATE      = 0
COL_TIME      = 1
COL_DAY       = 2
COL_CONTENT   = 3
COL_POST_TYPE = 4
COL_CAPTION   = 5
COL_HASHTAGS  = 6
COL_MEDIA_URL = 7
COL_STATUS    = 8
COL_POST_ID   = 9


def col(row, idx, default=""):
    return row[idx].strip() if idx < len(row) else default


def parse_dt(date_str: str, time_str: str) -> datetime:
    naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return naive.replace(tzinfo=AR_TZ)


def publish(row: list, dry_run: bool):
    post_type = col(row, COL_POST_TYPE) or "reel"
    # no fallback caption: a hardcoded default posted the same generic ad
    # 46 times (rows filled with dates but no caption, cleaned 2026-07-09)
    caption   = col(row, COL_CAPTION)
    media_url = col(row, COL_MEDIA_URL)
    hashtags  = col(row, COL_HASHTAGS)

    if not caption.strip():
        print("    SKIP — fila sin caption")
        return None, None
    if not media_url:
        print("    SKIP — no Media URL set in sheet")
        return None, None

    # Handle local files: check if it's a local path and upload to Drive first
    if not media_url.startswith(("http://", "https://")):
        local_path = ROOT / media_url.strip()
        if local_path.exists():
            print(f"    Local file detected: {media_url}")
            from googleapiclient.http import MediaFileUpload
            from tools.sheets_client import get_services
            
            _, drive = get_services()
            
            # Upload to Drive
            file_metadata = {
                'name': local_path.name,
                'mimeType': 'image/png' if local_path.suffix.lower() == '.png' else 'video/mp4'
            }
            media_obj = MediaFileUpload(str(local_path), mimetype=file_metadata['mimeType'])
            file = drive.files().create(body=file_metadata, media_body=media_obj, fields='id').execute()
            file_id = file.get('id')
            
            # Make it public
            drive.permissions().create(
                fileId=file_id,
                body={'kind': 'drive#permission', 'role': 'reader', 'type': 'anyone'},
                fields='id'
            ).execute()
            
            media_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            print(f"    Uploaded to Drive: {file_id}")

            # Upload story version if it exists
            story_path = local_path.parent / (local_path.stem + "_story" + local_path.suffix)
            if story_path.exists():
                s_obj = MediaFileUpload(str(story_path), mimetype='image/png')
                s_file = drive.files().create(body={'name': story_path.name, 'mimeType': 'image/png'}, media_body=s_obj, fields='id').execute()
                s_id = s_file.get('id')
                drive.permissions().create(fileId=s_id, body={'kind': 'drive#permission', 'role': 'reader', 'type': 'anyone'}, fields='id').execute()
                story_url = f"https://drive.google.com/uc?export=download&id={s_id}"
                print(f"story_url={story_url}")
        else:
            print(f"    ERROR: Local file not found: {local_path}")
            return None, None

    env = os.environ.copy()
    env["FACEBOOK_PAGE_ID"] = os.getenv("STORM_FACEBOOK_PAGE_ID", "")
    env["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = os.getenv("STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    cmd = [
        sys.executable, str(ROOT / "tools" / "post_instagram.py"),
        "--account", "storm",
        "--type", post_type,
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
    output = result.stdout.strip()
    if output:
        print(f"    {output[:200]}")
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr.strip()}")

    # Even on a non-zero exit (e.g. FB cross-post failed after IG succeeded),
    # an ID in stdout means the post IS live — never re-post it.
    for line in output.splitlines():
        for keyword in ("Media ID:", "reel ID:", "carousel ID:", "post ID:"):
            if keyword in line:
                return line.split(":")[-1].strip().split()[0], media_url
    return (None if result.returncode != 0 else "posted"), media_url


def update_status(sheets, sheet_id: str, row_idx: int, status: str, post_id: str):
    range_str = f"I{row_idx + 2}:J{row_idx + 2}"
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_str,
        valueInputOption="RAW",
        body={"values": [[status, post_id]]},
    ).execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force",   action="store_true", help="Post even if not yet due")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ENV_KEY)
    if not sheet_id:
        print(f"ERROR: {SHEET_ENV_KEY} not set in .env")
        sys.exit(1)

    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:J1000"
    ).execute().get("values", [])

    now = datetime.now(tz=AR_TZ)
    print(f"[Storm Digital] Checking calendar — {now.strftime('%Y-%m-%d %H:%M')} AR time")

    # never repeat a caption that already posted (46 clone rows slipped
    # through on 2026-07-09 — dup guard mirrors the fiestas publishers)
    posted_captions = {
        col(row, COL_CAPTION).strip()[:60].lower()
        for row in rows
        if col(row, COL_POST_ID).strip() or col(row, COL_STATUS) == "posted"
    }

    due = [
        (i, row, parse_dt(col(row, COL_DATE), col(row, COL_TIME)))
        for i, row in enumerate(rows)
        if col(row, COL_STATUS) in ("approved", "pending")
        and col(row, COL_DATE)
        and col(row, COL_TIME)
        and col(row, COL_CAPTION).strip()[:60].lower() not in posted_captions
        and (args.force or parse_dt(col(row, COL_DATE), col(row, COL_TIME)) <= now)
    ]

    # oldest first: with --force the whole calendar counts as due, and sheet
    # order let future posts jump the queue while overdue ones sat unposted
    due.sort(key=lambda t: t[2])

    if not due:
        print("Nothing due right now.")
        return

    # Cap at 1 post per run to avoid bot-detection triggers
    batch = due[:1]
    if len(due) > 1:
        print(f"{len(due)} due — publishing 1 (rate limit), rest deferred to next run\n")
    else:
        print(f"{len(due)} post(s) to publish:\n")

    posted = 0
    for i, row, post_dt in batch:
        content  = col(row, COL_CONTENT)
        media    = col(row, COL_MEDIA_URL)
        caption  = col(row, COL_CAPTION)
        hashtags = col(row, COL_HASHTAGS)
        print(f"  [{post_dt.strftime('%Y-%m-%d %H:%M')}] {content}")
        print(f"  Media: {media[:60] or '(none)'}")

        if not args.dry_run:
            update_status(sheets, sheet_id, i, "posting", "")

        post_id, resolved_media = publish(row, args.dry_run)
        notify_image = resolved_media or media

        if args.dry_run:
            notify(account="storm", caption=caption, image_url=notify_image, hashtags=hashtags, status="dry-run")
        elif post_id:
            update_status(sheets, sheet_id, i, "posted", post_id)
            print(f"    Sheet updated → posted (ID: {post_id})")
            posted += 1
            notify(account="storm", caption=caption, image_url=notify_image, hashtags=hashtags, status="posted", post_id=post_id)
        else:
            update_status(sheets, sheet_id, i, "error", "")
            print("    Sheet updated → error (won't auto-retry; fix and set back to pending)")
            notify(account="storm", caption=caption, image_url=notify_image, hashtags=hashtags, status="error")
        print()

    print(f"Done. {posted}/{len(batch)} published.")


if __name__ == "__main__":
    main()
