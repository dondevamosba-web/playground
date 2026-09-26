#!/usr/bin/env python3
"""
Cache small thumbnails of queued Instagram posts in Google Drive so the
"Mesa de Posteos" artifact can show them inline (the artifact viewer blocks
images from Instagram's CDN, but can read files from the owner's Drive).

For every pending/approved row in the unified approval sheet with no
thumbnail yet, downloads the image in col C (or grabs the first frame of a
video with ffmpeg), shrinks it to 480px JPEG, uploads it to the Drive folder
"Mesa de Posteos/thumbs" (private), and writes the Drive file ID in col I.

Run it before reviewing, or from cron right after the queue tools:
  python3 tools/cache_thumbnails.py
  python3 tools/cache_thumbnails.py --tab Fiestas
"""

import argparse
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from PIL import Image
from googleapiclient.http import MediaIoBaseUpload

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.upload_to_drive import get_or_create_folder

SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
TABS = ["Ola Digital", "Storm", "Fiestas", "Techno"]
WANTED = {"", "pending", "draft", "approved"}
COL_THUMB = "I"


def fetch_frame(url: str) -> Image.Image:
    """Image URL -> PIL image. Video URL -> its first frame (needs ffmpeg)."""
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    if "video" not in resp.headers.get("content-type", "") and ".mp4" not in url.split("?")[0]:
        return Image.open(io.BytesIO(resp.content))
    with tempfile.TemporaryDirectory() as d:
        src, out = Path(d) / "v.mp4", Path(d) / "f.jpg"
        src.write_bytes(resp.content)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "1", "-i", str(src), "-frames:v", "1", str(out)], check=True)
        return Image.open(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tab", help="Only this tab")
    args = parser.parse_args()

    sheets, drive = get_services()
    folder_id = get_or_create_folder(drive, "Mesa de Posteos/thumbs")
    done = failed = 0

    for tab in [args.tab] if args.tab else TABS:
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"'{tab}'!A1:I1000"
        ).execute().get("values", [])
        if not rows:
            continue
        updates = [] if len(rows[0]) > 8 and rows[0][8] else [{"range": f"'{tab}'!I1", "values": [["Thumb"]]}]

        for i, row in enumerate(rows[1:], start=2):
            row = row + [""] * (9 - len(row))
            if row[4].strip().lower() not in WANTED or row[8] or not row[2].startswith("http"):
                continue
            try:
                img = fetch_frame(row[2]).convert("RGB")
                img.thumbnail((480, 480))
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=80)
                buf.seek(0)
                f = drive.files().create(
                    body={"name": f"{tab}-row{i}.jpg", "parents": [folder_id]},
                    media_body=MediaIoBaseUpload(buf, mimetype="image/jpeg"),
                    fields="id",
                ).execute()
                updates.append({"range": f"'{tab}'!{COL_THUMB}{i}", "values": [[f["id"]]]})
                done += 1
            except Exception as e:  # expired CDN link, no ffmpeg, etc. — skip the row
                print(f"  {tab} fila {i}: sin miniatura ({e.__class__.__name__}: {str(e)[:80]})")
                failed += 1

        if updates:
            sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": updates}
            ).execute()

    print(f"{done} miniatura(s) nuevas, {failed} fallida(s).")


if __name__ == "__main__":
    main()
