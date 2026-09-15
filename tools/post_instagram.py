#!/usr/bin/env python3
"""
Post or schedule content to Instagram Business + Facebook Page via Graph API.
Supports single image, carousel, reel, and story post types.

Usage:
  python tools/post_instagram.py --type single --image-url URL --caption "..."
  python tools/post_instagram.py --type carousel --image-url URL1 URL2 URL3 --caption "..."
  python tools/post_instagram.py --type reel --video-url URL --caption "..."
  python tools/post_instagram.py --type story --image-url URL
  python tools/post_instagram.py --type story --video-url URL
  python tools/post_instagram.py --type single --image-url URL --caption "..." --schedule 2026-05-21T15:00:00+00:00
  python tools/post_instagram.py --account storm --type single --image-url URL --caption "..."
  python tools/post_instagram.py --type single --image-url URL --caption "..." --skip-facebook
"""

import argparse
import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_USER_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
BASE_URL = "https://graph.facebook.com/v19.0"

ACCOUNT_CONFIG = {
    "ola": {
        "ig_id_key": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "FACEBOOK_PAGE_ID",
    },
    "storm": {
        "ig_id_key": "STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "STORM_FACEBOOK_PAGE_ID",
    },
    "fiestas": {
        "ig_id_key": "FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "FIESTAS_FACEBOOK_PAGE_ID",
    },
    "techno": {
        "ig_id_key": "TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "TECHNO_FACEBOOK_PAGE_ID",
    },
    "empleo": {
        "ig_id_key": "OLA_EMPLEO_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "OLA_EMPLEO_FACEBOOK_PAGE_ID",
    },
    "talento": {
        "ig_id_key": "TALENTO_USA_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "fb_page_id_key": "TALENTO_USA_PAGE_ID",
    },
}


def select_account(account: str):
    global IG_USER_ID, FB_PAGE_ID
    account = (account or "ola").strip().lower()
    if account not in ACCOUNT_CONFIG:
        print(f"ERROR: Unknown account '{account}'. Supported accounts: {', '.join(ACCOUNT_CONFIG)}")
        sys.exit(1)

    IG_USER_ID = os.getenv(ACCOUNT_CONFIG[account]["ig_id_key"])
    FB_PAGE_ID = os.getenv(ACCOUNT_CONFIG[account]["fb_page_id_key"])
    print(f"Posting to Instagram account: {account}")


def check_credentials():
    if not ACCESS_TOKEN or not IG_USER_ID:
        print("ERROR: Missing credentials for the selected account in .env")
        print("  INSTAGRAM_ACCESS_TOKEN=...")
        print("  INSTAGRAM_BUSINESS_ACCOUNT_ID=... or STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID=...")
        print()
        print("See workflows/post_instagram.md for setup instructions.")
        sys.exit(1)


def build_caption(caption: str, hashtags: list[str]) -> str:
    if not hashtags:
        return caption
    tag_string = " ".join(f"#{t.lstrip('#')}" for t in hashtags)
    return f"{caption}\n\n{tag_string}"


def create_image_container(image_url: str, caption: str = None, is_carousel_item: bool = False) -> str:
    params = {
        "image_url": image_url,
        "access_token": ACCESS_TOKEN,
    }
    if is_carousel_item:
        params["is_carousel_item"] = "true"
    else:
        params["media_type"] = "IMAGE"
        if caption:
            params["caption"] = caption

    resp = requests.post(f"{BASE_URL}/{IG_USER_ID}/media", data=params)
    resp.raise_for_status()
    return resp.json()["id"]


def create_carousel_container(child_ids: list[str], caption: str) -> str:
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }
    resp = requests.post(f"{BASE_URL}/{IG_USER_ID}/media", data=params)
    resp.raise_for_status()
    return resp.json()["id"]


def create_reel_container(video_url: str, caption: str) -> str:
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
        "access_token": ACCESS_TOKEN,
    }
    resp = requests.post(f"{BASE_URL}/{IG_USER_ID}/media", data=params)
    resp.raise_for_status()
    return resp.json()["id"]


def wait_for_container(container_id: str, timeout: int = 120) -> bool:
    """Poll until container is FINISHED processing (needed for reels)."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print(f"Container processing failed: {resp.json()}")
            return False
        print(f"  Container status: {status} — waiting...")
        time.sleep(5)
    print("Timed out waiting for container to finish.")
    return False


def publish_container(container_id: str, schedule_time: str = None) -> dict:
    params = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }
    if schedule_time:
        # Convert ISO string to Unix timestamp
        dt = datetime.fromisoformat(schedule_time)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        params["scheduled_publish_time"] = int(dt.timestamp())
        params["status"] = "SCHEDULED"

    resp = requests.post(f"{BASE_URL}/{IG_USER_ID}/media_publish", data=params)
    resp.raise_for_status()
    return resp.json()


def get_page_access_token() -> str:
    """Exchange system user token for a Page access token."""
    resp = requests.get(
        f"{BASE_URL}/{FB_PAGE_ID}",
        params={"fields": "access_token", "access_token": ACCESS_TOKEN},
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise ValueError("Could not retrieve Page access token. Make sure the system user has Full Control over the page.")
    return token


def post_to_facebook(image_urls: list[str], caption: str, video_url: str = None) -> str:
    """Cross-post to Facebook Page. Returns the FB post ID."""
    if not FB_PAGE_ID:
        print("  [FB] FACEBOOK_PAGE_ID not set — skipping Facebook post")
        return None

    page_token = get_page_access_token()

    if video_url:
        params = {
            "file_url": video_url,
            "description": caption,
            "access_token": page_token,
        }
        resp = requests.post(f"{BASE_URL}/{FB_PAGE_ID}/videos", data=params)
    elif image_urls and len(image_urls) > 1:
        # Post cover slide + caption to Facebook (FB doesn't have Instagram-style carousels)
        params = {
            "url": image_urls[0],
            "message": caption,
            "access_token": page_token,
        }
        resp = requests.post(f"{BASE_URL}/{FB_PAGE_ID}/photos", data=params)
    else:
        params = {
            "url": image_urls[0],
            "message": caption,
            "access_token": page_token,
        }
        resp = requests.post(f"{BASE_URL}/{FB_PAGE_ID}/photos", data=params)

    if not resp.ok:
        print(f"  [FB] Error {resp.status_code}: {resp.json()}")
        resp.raise_for_status()
    fb_id = resp.json().get("id") or resp.json().get("post_id")
    print(f"  [FB] Published to Facebook Page — ID: {fb_id}")
    return fb_id


def get_media_permalink(media_id: str) -> str:
    resp = requests.get(
        f"{BASE_URL}/{media_id}",
        params={"fields": "permalink", "access_token": ACCESS_TOKEN},
    )
    resp.raise_for_status()
    return resp.json().get("permalink", "")


def post_single(image_url: str, caption: str, schedule_time: str = None, dry_run: bool = False, skip_facebook: bool = False):
    print(f"Creating single image post...")
    print(f"image_url={image_url}")
    if dry_run:
        print(f"[DRY RUN] Would create container: image_url={image_url}, caption={caption[:80]}...")
        return

    container_id = create_image_container(image_url, caption=caption)
    print(f"  Container created: {container_id}")

    result = publish_container(container_id, schedule_time)
    media_id = result["id"]

    if schedule_time:
        print(f"Scheduled post ID: {media_id} at {schedule_time}")
    else:
        permalink = get_media_permalink(media_id)
        print(f"Published to Instagram! Media ID: {media_id}")
        print(f"Permalink: {permalink}")
        if not skip_facebook:
            post_to_facebook([image_url], caption)


def post_carousel(image_urls: list[str], caption: str, schedule_time: str = None, dry_run: bool = False, skip_facebook: bool = False):
    if len(image_urls) < 2 or len(image_urls) > 10:
        print("ERROR: Carousel requires 2–10 images.")
        sys.exit(1)

    print(f"Creating carousel post with {len(image_urls)} images...")
    if dry_run:
        print(f"[DRY RUN] Would create {len(image_urls)} item containers, then carousel container")
        print(f"  Caption: {caption[:80]}...")
        return

    child_ids = []
    for i, url in enumerate(image_urls, 1):
        cid = create_image_container(url, is_carousel_item=True)
        print(f"  Item {i}/{len(image_urls)} container: {cid}")
        child_ids.append(cid)

    carousel_id = create_carousel_container(child_ids, caption)
    print(f"  Carousel container: {carousel_id}")

    result = publish_container(carousel_id, schedule_time)
    media_id = result["id"]

    if schedule_time:
        print(f"Scheduled carousel ID: {media_id} at {schedule_time}")
    else:
        permalink = get_media_permalink(media_id)
        print(f"Published carousel to Instagram! Media ID: {media_id}")
        print(f"Permalink: {permalink}")
        if not skip_facebook:
            post_to_facebook(image_urls, caption)


def create_story_container(image_url: str = None, video_url: str = None) -> str:
    params = {"access_token": ACCESS_TOKEN, "media_type": "STORIES"}
    if image_url:
        params["image_url"] = image_url
    elif video_url:
        params["video_url"] = video_url
    else:
        raise ValueError("Either image_url or video_url is required for a story")
    resp = requests.post(f"{BASE_URL}/{IG_USER_ID}/media", data=params)
    resp.raise_for_status()
    return resp.json()["id"]


def post_story(image_url: str = None, video_url: str = None, dry_run: bool = False):
    print("Creating story post...")
    if dry_run:
        src = f"image_url={image_url}" if image_url else f"video_url={video_url}"
        print(f"[DRY RUN] Would create story container: {src}")
        return

    container_id = create_story_container(image_url=image_url, video_url=video_url)
    print(f"  Container created: {container_id}")

    if video_url:
        print("  Waiting for video processing...")
        if not wait_for_container(container_id):
            print("ERROR: Story video container failed to process.")
            sys.exit(1)

    result = publish_container(container_id)
    media_id = result["id"]
    permalink = get_media_permalink(media_id)
    print(f"Published story to Instagram! Media ID: {media_id}")
    print(f"Permalink: {permalink}")


def post_reel(video_url: str, caption: str, schedule_time: str = None, dry_run: bool = False, skip_facebook: bool = False):
    print(f"Creating reel post...")
    if dry_run:
        print(f"[DRY RUN] Would create reel container: video_url={video_url}, caption={caption[:80]}...")
        return

    container_id = create_reel_container(video_url, caption)
    print(f"  Reel container created: {container_id}")
    print(f"  Waiting for video processing...")

    if not wait_for_container(container_id):
        print("ERROR: Video container failed to process.")
        sys.exit(1)

    result = publish_container(container_id, schedule_time)
    media_id = result["id"]

    if schedule_time:
        print(f"Scheduled reel ID: {media_id} at {schedule_time}")
    else:
        permalink = get_media_permalink(media_id)
        print(f"Published reel to Instagram! Media ID: {media_id}")
        print(f"Permalink: {permalink}")
        if not skip_facebook:
            post_to_facebook([], caption, video_url=video_url)


def main():
    parser = argparse.ArgumentParser(description="Post to Instagram via Graph API")
    parser.add_argument("--type", required=True, choices=["single", "carousel", "reel", "story"])
    parser.add_argument("--caption", default="")
    parser.add_argument("--image-url", nargs="+", dest="image_urls")
    parser.add_argument("--video-url", dest="video_url")
    parser.add_argument("--hashtags", nargs="+", default=[])
    parser.add_argument("--schedule", dest="schedule_time", help="ISO 8601 datetime e.g. 2026-05-21T15:00:00+00:00")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-facebook", action="store_true", help="Skip cross-posting to Facebook Page")
    parser.add_argument("--account", default="ola", choices=["ola", "storm", "fiestas", "techno", "empleo", "talento"], help="Select the Instagram/Facebook account to post to")
    args = parser.parse_args()

    select_account(args.account)
    if args.type != "story" and not args.caption:
        print("ERROR: --caption is required for this post type")
        sys.exit(1)

    if not args.dry_run:
        check_credentials()

    caption = build_caption(args.caption, args.hashtags)

    if args.type == "single":
        if not args.image_urls:
            print("ERROR: --image-url required for single post")
            sys.exit(1)
        post_single(args.image_urls[0], caption, args.schedule_time, args.dry_run, args.skip_facebook)

    elif args.type == "carousel":
        if not args.image_urls:
            print("ERROR: --image-url (multiple) required for carousel post")
            sys.exit(1)
        post_carousel(args.image_urls, caption, args.schedule_time, args.dry_run, args.skip_facebook)

    elif args.type == "reel":
        if not args.video_url:
            print("ERROR: --video-url required for reel post")
            sys.exit(1)
        post_reel(args.video_url, caption, args.schedule_time, args.dry_run, args.skip_facebook)

    elif args.type == "story":
        if not args.image_urls and not args.video_url:
            print("ERROR: --image-url or --video-url required for story post")
            sys.exit(1)
        image_url = args.image_urls[0] if args.image_urls else None
        post_story(image_url=image_url, video_url=args.video_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
