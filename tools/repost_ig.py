#!/usr/bin/env python3
"""
Download media from IG posts, upload to Google Drive, generate repost caption, queue for approval.

Works with images, videos/reels, and carousels. Skips posts already in the approval sheet.

Usage:
  python3 tools/repost_ig.py --shortcodes DZNZgKlEee6 DY7bIOIDrZs
  python3 tools/repost_ig.py --accounts musicaelectronica.club fiestas.electronicas.ba --limit 6
  python3 tools/repost_ig.py --from-json .tmp/ig_posts.json   # repost event posts from scraped file
  python3 tools/repost_ig.py --accounts underclub.bsas --limit 9 --dry-run
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import instaloader
import requests as req_lib
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from tools.sheets_client import get_services
from tools.generate_event_caption import generate_caption
from tools.queue_event_posts import (
    existing_event_keys, append_rows, now_ar,
    SHEET_ID_ENV, HEADERS,
)

DRIVE_FOLDER = "Fiestas Electronicas/Reposts"
MEDIA_TMP = ROOT / ".tmp" / "ig_media"

EVENT_KEYWORDS = [
    "fiesta", "party", "evento", "event", "dj", "techno", "house", "electróni",
    "electroni", "ticket", "entrada", "venue", "club", "boliche", "after",
    "lineup", "presenta", "pres.", "open to close", "live set", "arena",
    "festival", "rave", "baile", "pista",
]

REPOST_SYSTEM_PROMPT = """Sos un copywriter para una cuenta de Instagram de fiestas electrónicas en Argentina.
Tu voz es underground, directa, no corporativa. Escribís en español rioplatense.

Esta es una publicación compartida de otra cuenta de la escena electrónica de Buenos Aires.
Reescribí el contenido como si fuera tuyo, manteniendo la info del evento pero con tu voz.

Reglas de estilo:
- Nunca empieces una oración con ¿ (sin signo de apertura de interrogación)
- Sin emojis al principio de la oración
- Formato fechas argentino: sábado 7 de junio
- Horarios con h: 23h, no 11pm
- Tono: conciso, con onda, evocador
- Terminá el feed caption con la atribución: "Vía @{source_account}"
- Luego agregá hashtags en una línea aparte

Para el feed caption: 3–5 oraciones con info del evento + atribución + hashtags.
Para el story caption: 1–2 líneas muy cortas. Sin hashtags.

Respondé SOLO con JSON válido:
{{"feed_caption": "...", "story_caption": "..."}}"""


def looks_like_event(caption: str) -> bool:
    if not caption:
        return False
    low = caption.lower()
    return any(kw in low for kw in EVENT_KEYWORDS)


def get_or_create_drive_folder(drive, folder_path: str) -> str:
    parts = [p for p in folder_path.strip("/").split("/") if p]
    parent_id = "root"
    for part in parts:
        query = (f"name='{part}' and mimeType='application/vnd.google-apps.folder' "
                 f"and '{parent_id}' in parents and trashed=false")
        results = drive.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])
        if files:
            parent_id = files[0]["id"]
        else:
            folder = drive.files().create(
                body={"name": part, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
                fields="id",
            ).execute()
            parent_id = folder["id"]
    return parent_id


def upload_to_drive(drive, local_path: Path, folder_id: str) -> str:
    mime = "video/mp4" if local_path.suffix.lower() == ".mp4" else "image/jpeg"
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    file = drive.files().create(
        body={"name": local_path.name, "parents": [folder_id]},
        media_body=media,
        fields="id",
    ).execute()
    drive.permissions().create(fileId=file["id"], body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?export=download&id={file['id']}"


def download_media(url: str, dest: Path) -> Path:
    r = req_lib.get(url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    return dest


def process_post(post: instaloader.Post, L: instaloader.Instaloader,
                 drive, folder_id: str, source_account: str) -> dict | None:
    sc = post.shortcode
    caption_text = post.caption or ""

    if not looks_like_event(caption_text):
        return None

    MEDIA_TMP.mkdir(parents=True, exist_ok=True)
    media_urls = []
    post_type = "single"

    if post.typename == "GraphSidecar":
        post_type = "carousel"
        for node in post.get_sidecar_nodes():
            url = node.video_url if node.is_video else node.display_url
            ext = ".mp4" if node.is_video else ".jpg"
            local = MEDIA_TMP / f"{sc}_{len(media_urls)}{ext}"
            try:
                download_media(url, local)
                drive_url = upload_to_drive(drive, local, folder_id)
                media_urls.append(drive_url)
                local.unlink(missing_ok=True)
            except Exception as e:
                print(f"    WARN carousel item failed: {e}")
    elif post.is_video:
        post_type = "reel"
        local = MEDIA_TMP / f"{sc}.mp4"
        try:
            download_media(post.video_url, local)
            url = upload_to_drive(drive, local, folder_id)
            media_urls.append(url)
            local.unlink(missing_ok=True)
        except Exception as e:
            print(f"    WARN video download failed: {e}")
            return None
    else:
        local = MEDIA_TMP / f"{sc}.jpg"
        try:
            download_media(post.url, local)
            url = upload_to_drive(drive, local, folder_id)
            media_urls.append(url)
            local.unlink(missing_ok=True)
        except Exception as e:
            print(f"    WARN image download failed: {e}")
            return None

    if not media_urls:
        return None

    # Generate repost caption
    system = REPOST_SYSTEM_PROMPT.replace("{source_account}", source_account)
    from tools.claude_call import call_claude
    import re
    event_name = caption_text[:60].split("\n")[0].strip()
    prompt = f"""Repost de @{source_account}. Caption original:\n\n{caption_text[:800]}"""
    raw = call_claude(prompt, system_prompt=system)
    try:
        captions = json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        captions = json.loads(match.group()) if match else {"feed_caption": raw, "story_caption": ""}

    return {
        "shortcode": sc,
        "source_account": source_account,
        "post_url": f"https://www.instagram.com/p/{sc}/",
        "date": str(post.date.date()),
        "post_type": post_type,
        "image_url": media_urls[0],
        "extra_media_urls": media_urls[1:],
        "feed_caption": captions.get("feed_caption", ""),
        "story_caption": captions.get("story_caption", ""),
        "original_caption": caption_text[:300],
    }


def build_sheet_row(p: dict) -> list:
    return [
        now_ar(),
        f"IG @{p['source_account']} ({p['post_type']})",
        p["shortcode"],
        p["date"],
        "",
        "Buenos Aires",
        "",
        p["feed_caption"],
        p["story_caption"],
        p["image_url"],
        p["post_url"],
        "pending",
        "",
        f"Original: {p['original_caption']}",
    ]


def main():
    parser = argparse.ArgumentParser(description="Download IG media and queue reposts")
    parser.add_argument("--shortcodes", nargs="+", help="Specific post shortcodes")
    parser.add_argument("--accounts", nargs="+", help="IG handles to scrape")
    parser.add_argument("--from-json", help="Read shortcodes from .tmp/ig_posts.json")
    parser.add_argument("--limit", type=int, default=9, help="Posts per account to check")
    parser.add_argument("--dry-run", action="store_true", help="Download + caption but don't write to sheet")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ID_ENV, "").strip()
    if not sheet_id:
        print(f"ERROR: {SHEET_ID_ENV} not set in .env")
        sys.exit(1)

    sheets_svc, drive_svc = get_services()
    known = existing_event_keys(sheets_svc, sheet_id)
    print(f"Sheet has {len(known)} existing entries")

    folder_id = get_or_create_drive_folder(drive_svc, DRIVE_FOLDER)

    L = instaloader.Instaloader(
        quiet=True, download_pictures=False, download_videos=False,
        download_video_thumbnails=False, save_metadata=False,
    )

    posts_to_process: list[tuple[instaloader.Post, str]] = []

    # From specific shortcodes
    if args.shortcodes:
        for sc in args.shortcodes:
            try:
                post = instaloader.Post.from_shortcode(L.context, sc)
                posts_to_process.append((post, post.owner_username))
                time.sleep(1)
            except Exception as e:
                print(f"  FAIL {sc}: {e}")

    # From JSON file
    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            ig_posts = json.load(f)
        event_scs = [p["shortcode"] for p in ig_posts if p.get("is_event")]
        print(f"Loading {len(event_scs)} event posts from {args.from_json}")
        for sc in event_scs:
            try:
                post = instaloader.Post.from_shortcode(L.context, sc)
                posts_to_process.append((post, post.owner_username))
                time.sleep(1)
            except Exception as e:
                print(f"  FAIL {sc}: {e}")

    # From accounts
    if args.accounts:
        for handle in args.accounts:
            handle = handle.lstrip("@")
            print(f"Scraping @{handle}...")
            try:
                profile = instaloader.Profile.from_username(L.context, handle)
                count = 0
                for post in profile.get_posts():
                    if count >= args.limit:
                        break
                    if looks_like_event(post.caption or ""):
                        posts_to_process.append((post, handle))
                        count += 1
                    time.sleep(1.5)
                print(f"  {count} event posts queued from @{handle}")
            except Exception as e:
                print(f"  FAIL @{handle}: {e}")

    if not posts_to_process:
        print("Nothing to process.")
        return

    rows = []
    for post, source in posts_to_process:
        sc = post.shortcode
        key = (sc, str(post.date.date()))
        if key in known:
            print(f"  SKIP (already queued): {sc}")
            continue

        print(f"  Processing {sc} from @{source} ({post.typename})...")
        result = process_post(post, L, drive_svc, folder_id, source)
        if result:
            rows.append(build_sheet_row(result))
            print(f"    OK — {result['post_type']} queued")
        else:
            print(f"    SKIP — not an event post or media download failed")
        time.sleep(2)

    if not rows:
        print("No new posts to queue.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would queue {len(rows)} posts")
        return

    append_rows(sheets_svc, sheet_id, rows)
    print(f"\nQueued {len(rows)} reposts → https://docs.google.com/spreadsheets/d/{sheet_id}/edit")


if __name__ == "__main__":
    main()
