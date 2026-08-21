#!/usr/bin/env python3
"""
Publish a story for one IG account after a feed post goes live.
- Downloads the feed image, converts to 1080×1920 via post_to_story.py logic,
  uploads to Drive (public link), then posts to /{ig_id}/media with media_type=STORIES.
- Called automatically from publish_all_approved.py after each successful post.
- Can also be run standalone for any media URL.

Usage (standalone):
  python3 tools/publish_story.py --account "Ola Digital" --image-url "https://..." [--caption "texto"]
  python3 tools/publish_story.py --account Fiestas --image-url "https://..." --no-caption
"""
import argparse
import io
import os
import sys
import time
import requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from PIL import Image, ImageFilter
from googleapiclient.http import MediaIoBaseUpload
from upload_to_drive import get_drive_service, get_or_create_folder, make_public, get_public_url

TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
GRAPH = "https://graph.facebook.com/v19.0"

ACCOUNTS = {
    "Ola Digital": os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Storm":       os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Fiestas":     os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Techno":      os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
}

STORY_W, STORY_H = 1080, 1920


def make_story_image(image_url: str) -> bytes:
    """Download feed image, return 1080×1920 PNG bytes with blurred fill background."""
    r = requests.get(image_url, timeout=30)
    r.raise_for_status()
    post = Image.open(io.BytesIO(r.content)).convert("RGB")

    # blurred fill background
    bg = post.resize((STORY_W, int(STORY_W * post.height / post.width)))
    if bg.height < STORY_H:
        bg = bg.resize((int(STORY_H * bg.width / bg.height), STORY_H))
    bx = (bg.width - STORY_W) // 2
    by = (bg.height - STORY_H) // 2
    bg = bg.crop((bx, by, bx + STORY_W, by + STORY_H))
    bg = bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.55))

    # centred feed post (960px wide)
    pw = 960
    ph = int(pw * post.height / post.width)
    post = post.resize((pw, ph))
    px = (STORY_W - pw) // 2
    py = (STORY_H - ph) // 2
    bg.paste(post, (px, py))

    buf = io.BytesIO()
    bg.save(buf, format="PNG")
    return buf.getvalue()


def upload_to_drive(png_bytes: bytes, filename: str) -> str:
    """Upload PNG to Drive Stories folder, make public, return download URL."""
    service = get_drive_service()
    folder_id = get_or_create_folder(service, "Instagram/Stories")
    media = MediaIoBaseUpload(io.BytesIO(png_bytes), mimetype="image/png", resumable=False)
    file = service.files().create(
        body={"name": filename, "parents": [folder_id]},
        media_body=media, fields="id").execute()
    make_public(service, file["id"])
    return get_public_url(file["id"])


def post_story(ig_id: str, image_url: str) -> str | None:
    """Post a story image to IG. Returns media id or None on error."""
    r = requests.post(f"{GRAPH}/{ig_id}/media", data={
        "media_type": "STORIES",
        "image_url": image_url,
        "access_token": TOKEN,
    })
    res = r.json()
    if "id" not in res:
        print(f"    STORY ERROR creating container: {res}")
        return None
    time.sleep(3)
    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish", data={
        "creation_id": res["id"],
        "access_token": TOKEN,
    })
    res2 = r2.json()
    if "id" not in res2:
        print(f"    STORY ERROR publishing: {res2}")
        return None
    return res2["id"]


def publish_story_for_post(account: str, image_url: str, post_media_id: str, dry_run=False) -> str | None:
    """Full pipeline: make story image → Drive → IG story. Called from publish_all_approved."""
    if dry_run:
        print(f"    [dry-run] Would post story for {account}")
        return "dry-run"
    try:
        png = make_story_image(image_url)
        filename = f"story_{account.lower().replace(' ', '_')}_{post_media_id}.png"
        story_url = upload_to_drive(png, filename)
        story_id = post_story(ACCOUNTS[account], story_url)
        return story_id
    except Exception as e:
        print(f"    STORY exception ({account}): {e}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, choices=list(ACCOUNTS))
    ap.add_argument("--image-url", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    story_id = publish_story_for_post(a.account, a.image_url, "manual", dry_run=a.dry_run)
    if story_id:
        print(f"Story posted: {story_id}")


if __name__ == "__main__":
    main()
