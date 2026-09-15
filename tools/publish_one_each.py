#!/usr/bin/env python3
"""
Publish exactly 1 post from each of the 5 accounts (Ola, Storm, Fiestas, Techno, Empleo).
After each feed post, shares it to the account's Story.
Designed to run 3x/day, 1 hour apart, via cron.

Usage:
  python3 tools/publish_one_each.py           # publish 1 post per account
  python3 tools/publish_one_each.py --dry-run # preview without posting
"""
import argparse, subprocess, sys, os, time
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))  # so `from tools.x import y` works when run as a script
AR_TZ = timezone(timedelta(hours=-3))


def pad_to_story(img_bytes: bytes) -> bytes:
    """Pad a square (or any) image to 1080x1920 with black bars for Stories."""
    import io
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    canvas = Image.new("RGB", (1080, 1920), (0, 0, 0))
    img.thumbnail((1080, 1080), Image.LANCZOS)
    x = (1080 - img.width) // 2
    y = (1920 - img.height) // 2
    canvas.paste(img, (x, y))
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def upload_story_image(img_bytes: bytes, name: str) -> str:
    """Upload padded story image to Drive and return public URL."""
    import io
    from googleapiclient.http import MediaIoBaseUpload
    from tools.sheets_client import get_services
    _, drive_svc = get_services()
    folder_id = os.environ.get("DRIVE_FOLDER_ID", "root")
    meta = {"name": f"story_{name}.jpg", "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype="image/jpeg")
    f = drive_svc.files().create(body=meta, media_body=media, fields="id").execute()
    fid = f["id"]
    drive_svc.permissions().create(fileId=fid, body={"role": "reader", "type": "anyone"}).execute()
    return f"https://drive.google.com/uc?export=download&id={fid}"


def share_to_story(ig_id: str, token: str, media_id: str, dry_run: bool = False, direct_url: str = "") -> bool:
    """Share a published feed post to Stories, padded to 9:16 so image isn't cropped."""
    import requests
    graph = "https://graph.facebook.com/v19.0"
    media_url = direct_url
    media_type = "IMAGE"
    # Only hit the API if we don't already have the URL
    if not media_url:
        for attempt in range(4):
            r = requests.get(f"{graph}/{media_id}", params={
                "fields": "media_url,thumbnail_url,media_type",
                "access_token": token,
            })
            info = r.json()
            media_type = info.get("media_type", "IMAGE")
            media_url = info.get("media_url") or info.get("thumbnail_url", "")
            if media_url:
                break
            if attempt < 3:
                time.sleep(8)
    if not media_url:
        print("  Story: no media_url after retries, skipping")
        return False
    if dry_run:
        print(f"  Story: [dry-run] would share {media_type} to story")
        return True
    if media_type == "VIDEO":
        payload = {"media_type": "STORIES", "video_url": media_url, "access_token": token}
    else:
        # Pad square image to 9:16 to avoid Instagram cropping it
        try:
            img_bytes = requests.get(media_url, timeout=10).content
            padded = pad_to_story(img_bytes)
            story_url = upload_story_image(padded, media_id[:20])
        except Exception as e:
            print(f"  Story: pad failed ({e}), using original")
            story_url = media_url
        payload = {"image_url": story_url, "media_type": "STORIES", "access_token": token}
    # Story share is a nice-to-have on top of the feed post, which already
    # succeeded by the time we get here — a bad/non-JSON response (timeout,
    # transient 5xx) must never crash the whole batch and skip remaining
    # accounts. Found 2026-07-22: an uncaught JSONDecodeError here aborted
    # publish_one_each.py after Fiestas, so Empleo and Talento USA never ran.
    try:
        r2 = requests.post(f"{graph}/{ig_id}/media", data=payload, timeout=30)
        res2 = r2.json()
    except Exception as e:
        print(f"  Story: container request failed — {e}")
        return False
    if "id" not in res2:
        print(f"  Story: container error — {res2}")
        return False
    time.sleep(2)
    try:
        r3 = requests.post(f"{graph}/{ig_id}/media_publish", data={"creation_id": res2["id"], "access_token": token}, timeout=30)
        res3 = r3.json()
    except Exception as e:
        print(f"  Story: publish request failed — {e}")
        return False
    if "id" in res3:
        print(f"  Story: ✓ {res3['id']}")
        return True
    print(f"  Story: publish error — {res3}")
    return False


def run(script: str, account: str, ig_id: str, extra_args: list = None, dry_run: bool = False) -> str | None:
    """Run a publisher script; returns the media_id if published, else None."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    cmd = [sys.executable, str(ROOT / "tools" / script), "--force"]
    if extra_args:
        cmd += extra_args
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip()
    print(f"\n[{account}]\n" + "\n".join(f"  {l}" for l in out.splitlines()[:14]))
    # Extract media ID from output
    media_id = None
    for line in out.splitlines():
        for kw in ("Media ID:", "post ID:", "reel ID:", "→ posted"):
            if kw in line:
                media_id = line.split(":")[-1].strip().split()[0]
    if not media_id:
        # Try to find "ID: <number>" pattern
        import re
        m = re.search(r'ID[:\s]+(\d{15,})', out)
        if m:
            media_id = m.group(1)
    # Extract URLs from output: story_url= takes priority over image_url= for story
    import re
    direct_url = ""
    story_url = ""
    for line in out.splitlines():
        if line.startswith("story_url="):
            m = re.search(r'story_url=(https?://[^\s,]+)', line)
            if m:
                story_url = m.group(1)
        elif not direct_url and ("image_url=" in line or "video_url=" in line):
            m = re.search(r'(?:image_url|video_url)=(https?://[^\s,]+)', line)
            if m:
                direct_url = m.group(1)
    if media_id and not dry_run:
        share_to_story(ig_id, token, media_id, dry_run, direct_url=story_url or direct_url)
    return media_id


def run_fiestas(dry_run: bool) -> str | None:
    """Fiestas inline publisher — cap at 1 post, future events only."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    sys.path.insert(0, str(ROOT))
    from tools.sheets_client import get_services
    import requests

    today  = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d")
    sheet_id = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    ig_id    = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    token    = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    graph    = "https://graph.facebook.com/v19.0"

    COL_EVENT_DATE, COL_FEED_CAP, COL_IMAGE_URL, COL_STATUS, COL_POST_ID = 3, 7, 9, 11, 12

    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Queue!A2:N500"
    ).execute().get("values", [])

    # Build set of already-posted event names (dedup by name prefix)
    posted_names = {
        r[2].strip()[:40].lower() for r in rows
        if len(r) > COL_POST_ID and r[COL_POST_ID].strip()
    }

    target = next(
        ((i + 2, r) for i, r in enumerate(rows)
         if len(r) > COL_STATUS
         and r[COL_STATUS].strip() == "approved"
         and (len(r) <= COL_POST_ID or not r[COL_POST_ID].strip())
         and (len(r) <= COL_EVENT_DATE or not r[COL_EVENT_DATE].strip()
              or r[COL_EVENT_DATE].strip() >= today)
         and (r[2].strip()[:40].lower() if len(r) > 2 else "") not in posted_names),
        None
    )

    if not target:
        print("\n[Fiestas]\n  Nada para publicar.")
        return None

    sheet_row, r = target
    name      = r[2] if len(r) > 2 else ""
    caption   = r[COL_FEED_CAP]  if len(r) > COL_FEED_CAP  else ""
    image_url = r[COL_IMAGE_URL] if len(r) > COL_IMAGE_URL else ""
    notes     = r[13] if len(r) > 13 else ""
    video_url = notes[6:].strip() if notes.startswith("VIDEO:") else ""

    print(f"\n[Fiestas]\n  → {name}" + (" (reel)" if video_url else ""))

    if not image_url and not video_url:
        print("  SKIP — sin imagen ni video")
        return None

    if dry_run:
        print("  [dry-run] OK")
        return None

    if video_url:
        resp = requests.post(f"{graph}/{ig_id}/media", data={
            "media_type": "REELS", "video_url": video_url,
            "caption": caption, "access_token": token,
        })
    else:
        resp = requests.post(f"{graph}/{ig_id}/media", data={
            "image_url": image_url, "caption": caption, "access_token": token,
        })
    res = resp.json()
    if "id" not in res:
        print(f"  ERROR container: {res}")
        return None
    if video_url:
        # reels need server-side processing before publish
        for _ in range(24):
            st = requests.get(f"{graph}/{res['id']}",
                              params={"fields": "status_code", "access_token": token}).json()
            if st.get("status_code") == "FINISHED":
                break
            if st.get("status_code") == "ERROR":
                print(f"  ERROR processing reel: {st}")
                return None
            time.sleep(5)
    time.sleep(2)
    resp2 = requests.post(f"{graph}/{ig_id}/media_publish", data={
        "creation_id": res["id"], "access_token": token,
    })
    res2 = resp2.json()
    if "id" not in res2:
        print(f"  ERROR publish: {res2}")
        return None

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={"valueInputOption": "RAW", "data": [
            {"range": f"Queue!L{sheet_row}", "values": [["posted"]]},
            {"range": f"Queue!M{sheet_row}", "values": [[res2["id"]]]},
        ]}
    ).execute()
    media_id = res2["id"]
    print(f"  ✓ Posted — {media_id}")
    share_to_story(ig_id, token, media_id, dry_run)
    return media_id


def run_empleo(dry_run: bool) -> str | None:
    """Empleo publisher — reads OLA_EMPLEO_CALENDAR_SHEET_ID."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    ig_id = os.environ.get("OLA_EMPLEO_INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    if not ig_id:
        print("\n[Empleo]\n  Sin account ID configurado.")
        return None
    return run("auto_post_ola_empleo.py", "Empleo", ig_id, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")

    now = datetime.now(tz=AR_TZ)
    print(f"=== publish_one_each — {now.strftime('%Y-%m-%d %H:%M')} AR ===")

    # run_fiestas() executes inline (not a subprocess like the others), so an
    # uncaught exception there — as happened 2026-07-22 — silently skips
    # every account after it. Wrap it so one account's failure never blocks
    # the rest of the batch.
    run("auto_post_from_calendar.py", "Ola Digital",
        os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""), dry_run=args.dry_run)
    run("auto_post_storm.py", "Storm",
        os.environ.get("STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID", ""), dry_run=args.dry_run)
    run("auto_post_techno.py", "Techno",
        os.environ.get("TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID", ""), dry_run=args.dry_run)
    try:
        run_fiestas(dry_run=args.dry_run)
    except Exception as e:
        print(f"\n[Fiestas]\n  ERROR (uncaught): {e}")
    run_empleo(dry_run=args.dry_run)
    run("auto_post_talento_usa.py", "Talento USA",
        os.environ.get("TALENTO_USA_INSTAGRAM_BUSINESS_ACCOUNT_ID", ""), dry_run=args.dry_run)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
