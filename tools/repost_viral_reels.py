#!/usr/bin/env python3
"""
Download viral IG reels with yt-dlp, generate caption with Claude, queue to Fiestas sheet.

Usage:
  python3 tools/repost_viral_reels.py --urls https://www.instagram.com/reel/DY3jkmMudyc/
  python3 tools/repost_viral_reels.py --shortcodes DY3jkmMudyc DZdApauMHjf
  python3 tools/repost_viral_reels.py --scout technomistery_ mixmag --limit 5
  python3 tools/repost_viral_reels.py --shortcodes DY3jkmMudyc --dry-run
"""
import argparse, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services
from tools.claude_call import call_claude
from googleapiclient.http import MediaFileUpload

SHEET_ID      = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
DRIVE_FOLDER  = "Fiestas Electronicas/Reposts"
YT_DLP        = str(next(
    (p for p in (ROOT / ".venv-win/Scripts/yt-dlp.exe", ROOT / ".venv/bin/yt-dlp") if p.exists()),
    ROOT / ".venv/bin/yt-dlp",
))

CAPTION_PROMPT = """Sos un copywriter para @fiestaselectronicasbuenosaires en Instagram.
Voz underground, directa, en español rioplatense. Sin corporativo.

Te pasan un reel viral de la escena electrónica/techno/dance. Escribí un caption propio
que conecte con la comunidad de Buenos Aires. Puede ser un comentario sobre lo que se ve,
una reflexión sobre la cultura de las fiestas, o algo que genere identificación.
No describas literalmente el video. Si el texto original está en inglés, traducí la idea al rioplatense.

Reglas:
- Nunca empieces con ¿
- Sin emojis al principio
- 1–3 oraciones máximo + atribución "Vía @{account}" + hashtags en línea aparte
- Hashtags: #fiestaselectronicas #buenosaires + 3–5 relevantes al contenido

Respondé SOLO con JSON válido:
{{"feed_caption": "...", "story_caption": "..."}}"""


def ytdlp_info(url: str) -> dict | None:
    r = subprocess.run(
        [YT_DLP, "--dump-json", "--no-playlist", url],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        print(f"    yt-dlp info failed: {r.stderr[:200]}")
        return None
    return json.loads(r.stdout)


def ytdlp_account_reels(handle: str, limit: int) -> list[str]:
    """Return shortcodes of the most-liked recent reels from an IG account.

    Uses the Graph API business_discovery (yt-dlp stopped supporting
    /reels/ listing pages, 2026-07). Only works for business/creator accounts.
    """
    import requests
    tok = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    ig = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    r = requests.get(f"https://graph.facebook.com/v21.0/{ig}", params={
        "fields": f"business_discovery.username({handle})"
                  "{media.limit(25){media_type,media_product_type,permalink,like_count}}",
        "access_token": tok}, timeout=30).json()
    if "error" in r:
        print(f"    business_discovery error: {r['error'].get('message', '')[:100]}")
        return []
    media = r.get("business_discovery", {}).get("media", {}).get("data", [])
    reels = [m for m in media
             if m.get("media_product_type") == "REELS" or m.get("media_type") == "VIDEO"]
    reels.sort(key=lambda m: m.get("like_count", 0), reverse=True)
    shortcodes = []
    for m in reels[:limit]:
        sc = m.get("permalink", "").rstrip("/").split("/")[-1]
        if sc:
            shortcodes.append(sc)
    return shortcodes


def download_reel(url: str, dest_dir: Path) -> Path | None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(dest_dir / "%(id)s.%(ext)s")
    r = subprocess.run(
        [YT_DLP, "-f", "mp4/best[ext=mp4]/best", "-o", out_tmpl, "--no-playlist", url],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        print(f"    download failed: {r.stderr[:200]}")
        return None
    # find the downloaded file
    for f in dest_dir.iterdir():
        if f.suffix in (".mp4", ".mkv", ".webm"):
            return f
    return None


def get_or_create_drive_folder(drive, folder_path: str) -> str:
    parts = [p for p in folder_path.strip("/").split("/") if p]
    parent_id = "root"
    for part in parts:
        q = (f"name='{part}' and mimeType='application/vnd.google-apps.folder' "
             f"and '{parent_id}' in parents and trashed=false")
        files = drive.files().list(q=q, fields="files(id)").execute().get("files", [])
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
    mime = "video/mp4"
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=True)
    file = drive.files().create(
        body={"name": local_path.name, "parents": [folder_id]},
        media_body=media, fields="id",
    ).execute()
    drive.permissions().create(fileId=file["id"], body={"type": "anyone", "role": "reader"}).execute()
    return f"https://drive.google.com/uc?export=download&id={file['id']}"


def generate_caption(description: str, account: str) -> dict:
    system = CAPTION_PROMPT.replace("{account}", account)
    prompt = f"Cuenta: @{account}\nDescripción original:\n{description[:600]}"
    # sonnet: creative caption with brand voice system prompt, not mechanical
    raw = call_claude(prompt, system_prompt=system, model="sonnet")
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {"feed_caption": raw, "story_caption": ""}


def existing_shortcodes(sheets) -> set:
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range="Queue!K2:K500"
    ).execute()
    rows = result.get("values", [])
    codes = set()
    for r in rows:
        if r:
            url = r[0]
            m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
            if m:
                codes.add(m.group(1))
    return codes


def append_rows(sheets, rows):
    sheets.spreadsheets().values().append(
        spreadsheetId=SHEET_ID, range="Queue!A1",
        valueInputOption="RAW", insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def now_ar():
    from datetime import datetime, timezone, timedelta
    return datetime.now(tz=timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M")


def process_shortcode(sc: str, drive, folder_id: str, tmp: Path, dry_run: bool) -> list | None:
    url = f"https://www.instagram.com/reel/{sc}/"
    print(f"\n  [{sc}] Fetching info...")
    info = ytdlp_info(url)
    if not info:
        return None

    account = info.get("uploader_id", "").lstrip("@") or info.get("uploader", "unknown")
    description = info.get("description", "")
    thumbnail = info.get("thumbnail", "")

    print(f"    @{account} — {description[:80]}")
    print(f"    Downloading video...")

    sc_tmp = tmp / sc
    video_path = download_reel(url, sc_tmp)
    if not video_path:
        return None

    print(f"    Uploading to Drive ({video_path.stat().st_size // 1024}KB)...")
    if not dry_run:
        drive_url = upload_to_drive(drive, video_path, folder_id)
    else:
        drive_url = "https://drive.google.com/dry-run"
    video_path.unlink(missing_ok=True)

    print(f"    Generating caption...")
    caps = generate_caption(description, account)
    feed_cap = caps.get("feed_caption", "")
    story_cap = caps.get("story_caption", "")
    print(f"    Caption: {feed_cap[:100]}")

    row = [
        now_ar(),
        f"IG @{account} (reel)",
        sc,
        "",  # event date
        "",  # venue
        "Buenos Aires",
        "",  # lineup
        feed_cap,
        story_cap,
        thumbnail,      # image (thumbnail for preview)
        url,            # source url
        "pending",
        "",
        f"VIDEO:{drive_url}",  # drive video in col N
    ]
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="+", help="Full IG reel URLs")
    parser.add_argument("--shortcodes", nargs="+", help="IG shortcodes")
    parser.add_argument("--scout", nargs="+", help="IG handles to scout for top reels")
    parser.add_argument("--limit", type=int, default=5, help="Reels per account when scouting")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets, drive = get_services()
    known = existing_shortcodes(sheets)
    print(f"Sheet has {len(known)} existing repost entries")

    folder_id = get_or_create_drive_folder(drive, DRIVE_FOLDER)
    tmp = ROOT / ".tmp" / "viral_reels"

    shortcodes = []
    if args.urls:
        for u in args.urls:
            m = re.search(r"/reel/([A-Za-z0-9_-]+)", u)
            if m:
                shortcodes.append(m.group(1))
    if args.shortcodes:
        shortcodes += args.shortcodes
    if args.scout:
        print(f"Scouting {args.scout}...")
        for handle in args.scout:
            scs = ytdlp_account_reels(handle.lstrip("@"), args.limit)
            print(f"  @{handle}: {scs}")
            shortcodes += scs

    shortcodes = [sc for sc in shortcodes if sc not in known]
    if not shortcodes:
        print("Nothing new to process.")
        return

    print(f"\n{len(shortcodes)} reel(s) to process")
    rows = []
    for sc in shortcodes:
        row = process_shortcode(sc, drive, folder_id, tmp, args.dry_run)
        if row:
            rows.append(row)
            print(f"    ✓ queued")
        time.sleep(2)

    if not rows:
        print("No rows to add.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would queue {len(rows)} reels")
        for r in rows:
            print(f"  {r[2]} — {r[7][:80]}")
        return

    append_rows(sheets, rows)
    print(f"\n✓ {len(rows)} reels queued → sheet")


if __name__ == "__main__":
    main()
