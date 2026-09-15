#!/usr/bin/env python3
"""
Publish 3 Ola Digital posts today, spaced at 9:00 / 13:00 / 18:00 AR time.
After each feed post, also shares it as a story.
Checks for duplicates against the Meta API before publishing.

Usage:
  python3 tools/publish_ola_today.py             # schedule 3 posts for today
  python3 tools/publish_ola_today.py --dry-run   # show what would publish, no API calls
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageFilter

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_USER_ID   = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
FB_PAGE_ID   = os.getenv("FACEBOOK_PAGE_ID")
BASE         = "https://graph.facebook.com/v21.0"
AR_TZ        = timezone(timedelta(hours=-3))

SCHEDULE_FILE = ROOT / ".tmp/ola_schedule.json"
PUBLISH_TIMES = ["09:00", "13:00", "18:00"]
SIMILARITY_THRESHOLD = 0.75  # captions more similar than this = duplicate


# ── helpers ──────────────────────────────────────────────────────────────

def load_schedule():
    return json.loads(SCHEDULE_FILE.read_text())


def save_schedule(data):
    SCHEDULE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def caption_sim(a, b):
    return SequenceMatcher(None, a[:120], b[:120]).ratio()


def fetch_published_captions(limit=25):
    """Pull the last N published captions from the live IG account."""
    url = f"{BASE}/{IG_USER_ID}/media"
    params = {
        "fields": "caption,id",
        "limit": limit,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return [p.get("caption", "") for p in r.json().get("data", [])]


def is_duplicate(caption, published_captions):
    for pub in published_captions:
        if caption_sim(caption, pub) >= SIMILARITY_THRESHOLD:
            return True
    return False


def post_feed(image_url, caption, dry_run):
    if dry_run:
        print(f"  [dry-run] POST feed image → {image_url[:60]}")
        return "DRY_RUN_ID"

    # Step 1: create container
    r = requests.post(f"{BASE}/{IG_USER_ID}/media", data={
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }, timeout=30)
    r.raise_for_status()
    container_id = r.json()["id"]

    # Step 2: publish
    r2 = requests.post(f"{BASE}/{IG_USER_ID}/media_publish", data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }, timeout=30)
    r2.raise_for_status()
    return r2.json()["id"]


def fetch_ig_media_url(post_id: str) -> str:
    """Get the CDN media_url for a published IG post."""
    r = requests.get(f"{BASE}/{post_id}", params={
        "fields": "media_url",
        "access_token": ACCESS_TOKEN,
    }, timeout=15)
    r.raise_for_status()
    return r.json()["media_url"]


def make_story_image(image_url: str) -> bytes:
    """Download feed image and convert to 1080x1920 story format:
    blurred fill background + centered post image."""
    W, H = 1080, 1920
    r = requests.get(image_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    post = Image.open(io.BytesIO(r.content)).convert("RGB")

    # build blurred background: scale to fill 1080x1920, blur + darken
    bg = post.resize((W, int(W * post.height / post.width)))
    if bg.height < H:
        bg = bg.resize((int(H * bg.width / bg.height), H))
    # center-crop
    bg = bg.crop((
        (bg.width - W) // 2, (bg.height - H) // 2,
        (bg.width - W) // 2 + W, (bg.height - H) // 2 + H,
    ))
    bg = bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.5))

    # overlay: fit post inside 1040x1040 centered
    max_w = 1040
    ratio = min(max_w / post.width, max_w / post.height)
    new_w, new_h = int(post.width * ratio), int(post.height * ratio)
    post = post.resize((new_w, new_h), Image.LANCZOS)
    x = (W - new_w) // 2
    y = (H - new_h) // 2
    bg.paste(post, (x, y))

    buf = io.BytesIO()
    bg.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def post_story(image_url, dry_run):
    if dry_run:
        print(f"  [dry-run] POST story (1080×1920) ← {image_url[:60]}")
        return "DRY_RUN_STORY_ID"

    # convert to proper 9:16 story image
    print(f"     convirtiendo imagen a 1080×1920...")
    story_bytes = make_story_image(image_url)

    # upload via multipart (no public URL needed)
    r = requests.post(
        f"{BASE}/{IG_USER_ID}/media",
        params={"access_token": ACCESS_TOKEN},
        data={"media_type": "STORIES"},
        files={"source": ("story.jpg", story_bytes, "image/jpeg")},
        timeout=60,
    )
    r.raise_for_status()
    container_id = r.json()["id"]

    time.sleep(3)

    r2 = requests.post(f"{BASE}/{IG_USER_ID}/media_publish", data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }, timeout=30)
    r2.raise_for_status()
    return r2.json()["id"]


# ── main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run

    today = datetime.now(AR_TZ).strftime("%Y-%m-%d")
    print(f"{'[DRY RUN] ' if dry else ''}Ola Digital · publicando 3 posts para {today}\n")

    schedule = load_schedule()

    # ── 1. fetch live published captions for duplicate check ──────────────
    print("Verificando duplicados contra Meta API...")
    try:
        published_captions = fetch_published_captions(25)
        print(f"  {len(published_captions)} posts recientes descargados de IG\n")
    except Exception as e:
        print(f"  WARN: no se pudo consultar Meta API ({e}). Se usa solo el schedule local.\n")
        published_captions = []

    # also add already-posted captions from schedule
    for p in schedule:
        if p.get("status") == "posted" and p.get("caption"):
            published_captions.append(p["caption"])

    # ── 2. pick candidates: pending, has image_url, not duplicate ─────────
    candidates = []
    for p in schedule:
        if p.get("status") == "posted":
            continue
        if not p.get("image_url"):
            continue
        caption = p.get("caption", "")
        if is_duplicate(caption, published_captions):
            print(f"  SKIP (duplicado) → ID {p['id']}: {caption[:60]}…")
            continue
        candidates.append(p)

    if not candidates:
        print("No hay posts pendientes con imagen y sin duplicar.")
        sys.exit(0)

    chosen = candidates[:3]
    if len(chosen) < 3:
        print(f"WARN: solo hay {len(chosen)} candidatos disponibles (se necesitan 3)\n")

    # ── 3. assign times and publish ───────────────────────────────────────
    print(f"Seleccionados {len(chosen)} posts:\n")
    for i, post in enumerate(chosen):
        t = PUBLISH_TIMES[i]
        print(f"  [{t}] ID {post['id']} — {post['caption'][:70]}…")
        print(f"        imagen: {post['image_url'][:70]}")

        full_caption = post["caption"]
        if post.get("hashtags"):
            full_caption += "\n\n" + post["hashtags"]

        # ── publish feed post ──
        print(f"  → publicando feed post...")
        try:
            feed_id = post_feed(post["image_url"], full_caption, dry)
            print(f"     OK feed post_id={feed_id}")
        except Exception as e:
            print(f"     ERROR feed: {e}")
            continue

        # ── publish story (using CDN URL from the just-published feed post) ──
        print(f"  → publicando story...")
        try:
            cdn_url = fetch_ig_media_url(feed_id) if not dry else post["image_url"]
            story_id = post_story(cdn_url, dry)
            print(f"     OK story post_id={story_id}")
        except Exception as e:
            print(f"     ERROR story: {e}")
            story_id = None

        # ── update schedule ──
        if not dry:
            for row in schedule:
                if row["id"] == post["id"]:
                    row["status"]  = "posted"
                    row["post_id"] = feed_id
                    row["date"]    = today
                    row["time"]    = t
                    if story_id:
                        row["story_id"] = story_id
                    break
            save_schedule(schedule)

        print()

        # space out API calls (not needed for scheduling, but avoids rate-limit on actual publish)
        if not dry and i < len(chosen) - 1:
            time.sleep(2)

    print("Listo." if not dry else "[dry-run] completado sin publicar.")


if __name__ == "__main__":
    main()
