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
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.notify_discord import notify

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


MIN_IMAGE_BYTES = 80_000   # < 80 KB = low-res thumbnail, reject
FRAGILE_PREFIXES = ("pisces.bbystatic.com",)  # always replace, serve wrong product
# CDNs that block HEAD but work fine for GET (Instagram fetches via GET)
TRUSTED_CDNS = ("apple.com", "amazon.com", "m.media-amazon.com",
                "samsung.com", "store.storeimages.cdn-apple.com",
                "i5.walmartimages.com", "images.samsung.com", "image-us.samsung.com",
                "drive.google.com")

def check_url(url: str, min_bytes: int = MIN_IMAGE_BYTES) -> bool:
    """Return True if URL is accessible. Trusted CDNs skip the HEAD check."""
    if any(cdn in url for cdn in TRUSTED_CDNS):
        return True  # these block HEAD but work for Instagram GET
    try:
        req = urllib.request.Request(url, method="HEAD",
              headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            if r.status != 200:
                return False
            size = int(r.headers.get("Content-Length", 0))
            return size == 0 or size >= min_bytes  # 0 = chunked, allow through
    except Exception:
        return False


def resolve_image(product: str, current_url: str) -> str:
    """Validate current_url; if broken/fragile/low-res, pull from pool."""
    is_fragile = any(d in current_url for d in FRAGILE_PREFIXES)
    if current_url and not is_fragile and check_url(current_url):
        return current_url
    if is_fragile:
        print(f"    ⚠ Fragile image source detected, replacing…")
    # URL broken or fragile — try pool
    try:
        from tools.techno_fix_all_images import find_pool
        pool = find_pool(product)
        if pool:
            for url in pool:
                if check_url(url):
                    print(f"    ⚠ Image replaced: {url[:70]}")
                    return url
    except Exception as e:
        print(f"    ⚠ Could not load image pool: {e}")
    return ""


def upload_local_to_drive(media_url: str) -> str:
    """If media_url is a local path, upload it to Drive and return a public URL."""
    local_path = ROOT / media_url.strip()
    if not local_path.exists():
        return media_url
    print(f"    Local file detected: {media_url}")
    from googleapiclient.http import MediaFileUpload

    _, drive = get_services()
    file_metadata = {
        'name': local_path.name,
        'mimeType': 'image/png' if local_path.suffix.lower() == '.png' else 'video/mp4'
    }
    media_obj = MediaFileUpload(str(local_path), mimetype=file_metadata['mimeType'])
    file = drive.files().create(body=file_metadata, media_body=media_obj, fields='id').execute()
    file_id = file.get('id')
    drive.permissions().create(
        fileId=file_id,
        body={'kind': 'drive#permission', 'role': 'reader', 'type': 'anyone'},
        fields='id'
    ).execute()
    uploaded_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"    Uploaded to Drive: {file_id}")
    return uploaded_url


def publish(row, dry_run):
    post_type = col(row, COL_POST_TYPE) or "single"
    caption   = col(row, COL_CAPTION)
    media_url = col(row, COL_MEDIA_URL)
    hashtags  = col(row, COL_HASHTAGS)
    product   = col(row, COL_PRODUCT)

    if not media_url:
        print("    SKIP — no Media URL set in sheet")
        return None, None

    if not media_url.startswith(("http://", "https://")):
        media_url = upload_local_to_drive(media_url)

    if post_type != "reel":
        media_url = resolve_image(product, media_url)
        if not media_url:
            print("    SKIP — image URL broken and no fallback found in pool")
            return None, None

    env = os.environ.copy()
    env["FACEBOOK_PAGE_ID"]                 = os.getenv("TECHNO_FACEBOOK_PAGE_ID", "")
    env["INSTAGRAM_BUSINESS_ACCOUNT_ID"]    = os.getenv("TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    cmd = [
        sys.executable, str(ROOT / "tools" / "post_instagram.py"),
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
    output = result.stdout.strip()
    if output:
        print(f"    {output[:200]}")
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr.strip()}")

    # Even on a non-zero exit (e.g. FB cross-post failed after IG succeeded),
    # an ID in stdout means the post IS live — never re-post it.
    for line in output.splitlines():
        for keyword in ("Media ID:", "post ID:", "reel ID:"):
            if keyword in line:
                return line.split(":")[-1].strip().split()[0], media_url
    return (None if result.returncode != 0 else "posted"), media_url


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

    # Products posted in the last 30 days — skip to avoid repeats
    recently_posted = set()
    for row in rows:
        if col(row, COL_STATUS) == "posted" and col(row, COL_DATE):
            try:
                posted_dt = parse_dt(col(row, COL_DATE), col(row, COL_TIME) or "00:00")
                if (now - posted_dt).days <= 30:
                    recently_posted.add(col(row, COL_PRODUCT).lower())
            except Exception:
                pass

    # never repeat: skip any caption already posted on this account
    # (Guido 2026-07-10: "para ninguna repitas nunca")
    posted_captions = {
        col(row, COL_CAPTION).strip()[:60].lower()
        for row in rows
        if col(row, COL_POST_ID).strip() or col(row, COL_STATUS) == "posted"
    }

    due = [
        (i, row, parse_dt(col(row, COL_DATE), col(row, COL_TIME)))
        for i, row in enumerate(rows)
        if col(row, COL_STATUS) in ("pending", "approved")
        and col(row, COL_CAPTION).strip()[:60].lower() not in posted_captions
        and col(row, COL_DATE)
        and col(row, COL_TIME)
        and col(row, COL_MEDIA_URL)
        and col(row, COL_PRODUCT).lower() not in recently_posted
        and (args.force or parse_dt(col(row, COL_DATE), col(row, COL_TIME)) <= now)
    ]

    # oldest first: with --force the whole calendar counts as due, and sheet
    # order let future posts jump the queue while overdue ones sat unposted
    due.sort(key=lambda t: t[2])

    if not due:
        print("Nothing due right now.")
        return

    batch = due[:1]
    if len(due) > 1:
        print(f"{len(due)} due — publishing 1 (rate limit), rest deferred to next run\n")
    else:
        print(f"{len(due)} post(s) to publish:\n")

    posted = 0
    for i, row, post_dt in batch:
        product  = col(row, COL_PRODUCT)
        brand    = col(row, COL_BRAND)
        media    = col(row, COL_MEDIA_URL)
        caption  = col(row, COL_CAPTION)
        hashtags = col(row, COL_HASHTAGS)
        print(f"  [{post_dt.strftime('%Y-%m-%d %H:%M')}] {brand.upper()} — {product}")
        print(f"  Media: {media[:60]}")

        if not args.dry_run:
            update_status(sheets, sheet_id, i, "posting", "")

        post_id, resolved_media = publish(row, args.dry_run)
        notify_image = resolved_media or media

        if args.dry_run:
            notify(account="techno", caption=caption, image_url=notify_image, hashtags=hashtags, status="dry-run")
        elif post_id:
            update_status(sheets, sheet_id, i, "posted", post_id)
            print(f"    Sheet updated → posted (ID: {post_id})")
            posted += 1
            notify(account="techno", caption=caption, image_url=notify_image, hashtags=hashtags, status="posted", post_id=post_id)
        else:
            update_status(sheets, sheet_id, i, "error", "")
            print("    Sheet updated → error (won't auto-retry; fix and set back to pending)")
            notify(account="techno", caption=caption, image_url=notify_image, hashtags=hashtags, status="error")
        print()

    print(f"Done. {posted}/{len(batch)} published.")


if __name__ == "__main__":
    main()
