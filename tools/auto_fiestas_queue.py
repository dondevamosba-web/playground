#!/usr/bin/env python3
"""
Daily Fiestas orchestrator: RA events + IG reposts from configured accounts,
branded 1080x1080 images uploaded to Drive, rows written straight to
Status="approved" (no manual review step — see workflows/fiestas/scrape_and_queue.md
for the reviewed/"pending" version, queue_event_posts.py).

Sources:
  - Resident Advisor Argentina (upcoming events)
  - Event-listing IG accounts (FIESTAS_REPOST_ACCOUNTS / default list below)
  - Viral/media IG accounts (FIESTAS_VIRAL_ACCOUNTS / default list below)

Usage:
  python3 tools/auto_fiestas_queue.py
  python3 tools/auto_fiestas_queue.py --skip-ra --skip-ig
  python3 tools/auto_fiestas_queue.py --dry-run
  python3 tools/auto_fiestas_queue.py --limit 6   # posts checked per IG account
"""

import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

import instaloader
import requests as req_lib
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.queue_event_posts import (
    get_or_create_sheet, existing_event_keys, append_rows, now_ar,
)
from tools.generate_event_caption import generate_caption
from tools.repost_ig import (
    looks_like_event, get_or_create_drive_folder, upload_to_drive,
    download_media, DRIVE_FOLDER,
)
from tools.claude_call import call_claude

MEDIA_TMP = ROOT / ".tmp" / "auto_fiestas_media"
BRAND_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_TAG = "@fiestas.electronicas"  # bottom-corner watermark; adjust to the real handle

# --- IG scrape ramp-up ------------------------------------------------------
# Instagram blocks scraping from datacenter IPs. Rather than guess a safe
# per-account post limit, start at 1 and add 1 more each calendar day; freeze
# the limit the moment Instagram signals a block instead of pushing further.
RAMP_STATE_FILE = ROOT / ".tmp" / "fiestas_ig_ramp_state.json"
RAMP_START = 1
RAMP_STEP = 1
RAMP_MAX = 10

BLOCK_EXCEPTIONS = (
    instaloader.exceptions.TooManyRequestsException,
    instaloader.exceptions.LoginRequiredException,
    instaloader.exceptions.ConnectionException,
)


class InstagramBlockedError(Exception):
    def __init__(self, handle: str, reason: str):
        self.handle = handle
        self.reason = reason
        super().__init__(f"@{handle}: {reason}")


def is_blocking_error(e: Exception) -> bool:
    if isinstance(e, BLOCK_EXCEPTIONS):
        return True
    msg = str(e).lower()
    return any(kw in msg for kw in ("429", "checkpoint", "rate limit", "please wait", "login required", "log in"))


def load_ramp_state() -> dict:
    if RAMP_STATE_FILE.exists():
        try:
            return json.loads(RAMP_STATE_FILE.read_text())
        except Exception:
            pass
    return {"date": None, "limit": RAMP_START, "flagged": False, "flagged_at": None, "flagged_reason": None}


def save_ramp_state(state: dict):
    RAMP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    RAMP_STATE_FILE.write_text(json.dumps(state, indent=2))


def get_daily_limit() -> int:
    """Today's per-account post limit: ramps up by RAMP_STEP/day, frozen after the first block."""
    state = load_ramp_state()
    today = now_ar()[:10]

    if state["flagged"]:
        print(f"IG ramp: frozen at limit={state['limit']} since first block on "
              f"{state['flagged_at']} (@{state.get('flagged_handle', '?')}: {state['flagged_reason']}). "
              f"Reset .tmp/fiestas_ig_ramp_state.json to resume ramping.")
        return state["limit"]

    if state["date"] != today:
        if state["date"] is not None:
            state["limit"] = min(state["limit"] + RAMP_STEP, RAMP_MAX)
        state["date"] = today
        save_ramp_state(state)

    print(f"IG ramp: day's per-account limit = {state['limit']} (not yet flagged)")
    return state["limit"]


def record_flag(handle: str, reason: str):
    state = load_ramp_state()
    if not state["flagged"]:
        state["flagged"] = True
        state["flagged_at"] = now_ar()
        state["flagged_handle"] = handle
        state["flagged_reason"] = reason
        save_ramp_state(state)
    print(f"\n*** FIRST FLAG HIT: @{handle} — {reason} ***")
    print(f"*** Ramp frozen at limit={state['limit']}. Stopping IG scraping for this run. ***")

DEFAULT_EVENT_ACCOUNTS = [
    "electronicmusictickets", "infoticketsarg", "baires.electronica",
    "technobuenosaires", "wearebombo", "ems_arg", "moonparkoficial", "nisfernandez",
]

DEFAULT_VIRAL_ACCOUNTS = [
    "mixmag", "boilerroom", "factmag", "rave.archive", "techno.community",
    # Remaining accounts from the daily brief — fill in the exact 19 handles here.
    # Left short deliberately: the prompt only named 5 of the 19 "viral" accounts.
]

VIRAL_CAPTION_SYSTEM = """Sos un copywriter para una cuenta de Instagram de fiestas electrónicas en Argentina.
Tu voz es underground, directa, no corporativa. Escribís en español rioplatense.

Este es un post viral de una cuenta internacional de la escena electrónica (medio, sello, o cuenta de cultura rave).
No es un evento local — es contenido de interés general para la audiencia (noticia, clip, meme, dato).
Escribí un caption corto adaptado a la audiencia de Buenos Aires, manteniendo la atribución.

Reglas de estilo:
- Nunca empieces una oración con ¿ (sin signo de apertura de interrogación)
- Formato fechas argentino si aplica
- Tono: conciso, con onda
- Terminá el feed caption con la atribución: "Vía @{source_account}"
- Agregá 3-5 hashtags en una línea aparte

Para el story caption: 1 línea muy corta. Sin hashtags.

Respondé SOLO con JSON válido:
{{"feed_caption": "...", "story_caption": "..."}}"""


def brand_image(local_path: Path) -> Path:
    """Resize/crop to 1080x1080 and stamp a bottom-corner watermark."""
    img = Image.open(local_path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((1080, 1080), Image.LANCZOS)

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([(0, 1000), (1080, 1080)], fill=(0, 0, 0, 140))
    try:
        font = ImageFont.truetype(BRAND_FONT, 34)
    except Exception:
        font = ImageFont.load_default()
    draw.text((24, 1020), BRAND_TAG, font=font, fill=(255, 255, 255, 255))

    out_path = local_path.with_name(local_path.stem + "_branded.jpg")
    img.save(out_path, "JPEG", quality=90)
    return out_path


def queue_ra_events(sheets, sheet_id, known, dry_run) -> list[list]:
    print("\nScraping Resident Advisor Argentina...")
    tmp = ROOT / ".tmp" / "auto_fiestas_ra.json"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    import subprocess
    result = subprocess.run(
        ["python3", str(ROOT / "tools" / "scrape_ra_events.py"), "--output", str(tmp)],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  WARN scrape_ra_events.py failed: {result.stderr.strip()[:300]}")
        return []

    events = json.loads(tmp.read_text()) if tmp.exists() else []
    print(f"  {len(events)} RA events scraped")

    rows = []
    for ev in events:
        key = (ev.get("name", "").strip(), ev.get("date", "").strip())
        if not key[0] or key in known:
            continue
        try:
            captioned = generate_caption(ev)
        except Exception as e:
            print(f"    Caption error for {ev.get('name')}: {e}")
            captioned = ev

        image_url = captioned.get("image_url", "")
        if image_url and not dry_run:
            try:
                MEDIA_TMP.mkdir(parents=True, exist_ok=True)
                local = MEDIA_TMP / f"ra_{abs(hash(key))}.jpg"
                download_media(image_url, local)
                branded = brand_image(local)
                _, drive_svc = get_services()
                folder_id = get_or_create_drive_folder(drive_svc, DRIVE_FOLDER)
                image_url = upload_to_drive(drive_svc, branded, folder_id)
            except Exception as e:
                print(f"    WARN branding/upload failed, keeping original image URL: {e}")

        rows.append([
            now_ar(), "Resident Advisor", ev.get("name", ""), ev.get("date", ""),
            ev.get("venue", ""), ev.get("city", "Buenos Aires"),
            ", ".join(ev.get("artists") or []),
            captioned.get("feed_caption", ""), captioned.get("story_caption", ""),
            image_url, ev.get("event_url", ""),
            "approved", "", "Auto-queued (daily pipeline)",
        ])
        known.add(key)
    return rows


def queue_ig_account(L, drive_svc, folder_id, handle, limit, is_event_account, known) -> list[list]:
    handle = handle.lstrip("@")
    print(f"  Scraping @{handle}...")
    rows = []
    try:
        profile = instaloader.Profile.from_username(L.context, handle)
    except Exception as e:
        if is_blocking_error(e):
            raise InstagramBlockedError(handle, str(e)[:200]) from e
        print(f"    FAIL @{handle}: {e}")
        return rows

    count = 0
    for post in profile.get_posts():
        if count >= limit:
            break
        caption_text = post.caption or ""
        if is_event_account and not looks_like_event(caption_text):
            time.sleep(1)
            continue

        sc = post.shortcode
        key = (sc, str(post.date.date()))
        if key in known:
            time.sleep(1)
            continue

        MEDIA_TMP.mkdir(parents=True, exist_ok=True)
        try:
            url = post.video_url if post.is_video else post.url
            ext = ".mp4" if post.is_video else ".jpg"
            local = MEDIA_TMP / f"{sc}{ext}"
            download_media(url, local)
            if not post.is_video:
                local = brand_image(local)
            image_url = upload_to_drive(drive_svc, local, folder_id)
        except Exception as e:
            if is_blocking_error(e):
                raise InstagramBlockedError(handle, str(e)[:200]) from e
            print(f"    WARN media failed for {sc}: {e}")
            time.sleep(1)
            continue

        if is_event_account:
            system = f"""Sos un copywriter para una cuenta de Instagram de fiestas electrónicas en Argentina.
Reescribí este post de @{handle} como repost propio, tono underground rioplatense.
Terminá con \"Vía @{handle}\" y hashtags en línea aparte.
Respondé SOLO con JSON: {{{{"feed_caption": "...", "story_caption": "..."}}}}"""
        else:
            system = VIRAL_CAPTION_SYSTEM.replace("{source_account}", handle)

        try:
            raw = call_claude(f"Caption original:\n\n{caption_text[:800]}", system_prompt=system)
            captions = json.loads(raw)
        except Exception:
            captions = {"feed_caption": caption_text[:200], "story_caption": ""}

        rows.append([
            now_ar(), f"IG @{handle}" + (" (event)" if is_event_account else " (viral)"),
            sc, str(post.date.date()), "", "Buenos Aires", "",
            captions.get("feed_caption", ""), captions.get("story_caption", ""),
            image_url, f"https://www.instagram.com/p/{sc}/",
            "approved", "", f"Auto-queued (daily pipeline). Original: {caption_text[:200]}",
        ])
        known.add(key)
        count += 1
        time.sleep(2)

    print(f"    {count} posts queued from @{handle}")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Auto-queue + auto-approve Fiestas posts (RA + IG reposts)")
    parser.add_argument("--skip-ra", action="store_true")
    parser.add_argument("--skip-ig", action="store_true")
    parser.add_argument("--limit", type=int, default=None,
                         help="Posts checked per IG account (default: ramps up 1/day, see get_daily_limit)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets_svc, drive_svc = get_services()
    sheet_id = get_or_create_sheet(sheets_svc, drive_svc)
    known = existing_event_keys(sheets_svc, sheet_id)
    print(f"Sheet has {len(known)} existing entries.")

    all_rows = []

    if not args.skip_ra:
        all_rows += queue_ra_events(sheets_svc, sheet_id, known, args.dry_run)

    if not args.skip_ig:
        event_accounts = [a.strip() for a in os.getenv("FIESTAS_REPOST_ACCOUNTS", "").split(",") if a.strip()] or DEFAULT_EVENT_ACCOUNTS
        viral_accounts = [a.strip() for a in os.getenv("FIESTAS_VIRAL_ACCOUNTS", "").split(",") if a.strip()] or DEFAULT_VIRAL_ACCOUNTS
        limit = args.limit if args.limit is not None else get_daily_limit()

        L = instaloader.Instaloader(
            quiet=True, download_pictures=False, download_videos=False,
            download_video_thumbnails=False, save_metadata=False,
        )
        folder_id = get_or_create_drive_folder(drive_svc, DRIVE_FOLDER)

        print(f"\nScraping {len(event_accounts)} event accounts + {len(viral_accounts)} viral accounts "
              f"(limit={limit}/account)...")
        try:
            for handle in event_accounts:
                all_rows += queue_ig_account(L, drive_svc, folder_id, handle, limit, True, known)
            for handle in viral_accounts:
                all_rows += queue_ig_account(L, drive_svc, folder_id, handle, limit, False, known)
        except InstagramBlockedError as e:
            record_flag(e.handle, e.reason)

    if not all_rows:
        print("\nNo new posts to queue.")
        return

    print(f"\n{len(all_rows)} new posts (auto-approved):")
    for r in all_rows:
        print(f"  [{r[1]}] {r[2]} — {r[3]}")

    if args.dry_run:
        print("\n[DRY RUN] Not writing to sheet.")
        return

    append_rows(sheets_svc, sheet_id, all_rows)
    print(f"\nQueued {len(all_rows)} posts (Status=approved) → https://docs.google.com/spreadsheets/d/{sheet_id}/edit")


if __name__ == "__main__":
    main()
