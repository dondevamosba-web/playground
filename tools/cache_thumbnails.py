#!/usr/bin/env python3
"""
Cache small thumbnails of upcoming Instagram posts in Google Drive so the
"Mesa de Posteos" artifact can show them inline (the artifact viewer blocks
images from Instagram's CDN and can't see files on this PC, but can read files
from the owner's Drive).

Covers the unified approval sheet (pending/approved rows) and the content
calendars (pending/preview_sent/approved rows dated from 7 days ago on). The
media can be a URL or a local path (relative to the repo or absolute). Videos
use their first frame (needs ffmpeg). Each thumbnail is a 480px JPEG in the
private Drive folder "Mesa de Posteos/thumbs"; its file ID goes in the row's
Thumb column (see tools/posting_sources.py).

  python3 tools/cache_thumbnails.py
"""

import io
import subprocess
import sys
import tempfile
from datetime import date, timedelta
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
from tools.posting_sources import (APPROVAL_SHEET_ID, APPROVAL_TABS, APPROVAL_COLS,
                                   CALENDARS, OPEN_STATUSES, col_letter)

WANTED = OPEN_STATUSES | {"approved"}
VIDEO = (".mp4", ".mov")


def load_image(media: str) -> Image.Image:
    """URL or local path -> PIL image. Videos -> their first frame (ffmpeg)."""
    if media.startswith("http"):
        resp = requests.get(media, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        is_video = "video" in resp.headers.get("content-type", "") or media.split("?")[0].lower().endswith(VIDEO)
        if not is_video:
            return Image.open(io.BytesIO(resp.content))
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp.write(resp.content)
        tmp.close()
        path = Path(tmp.name)
    else:
        path = Path(media)
        if not path.is_absolute():
            path = ROOT / path
        if path.suffix.lower() not in VIDEO:
            return Image.open(path)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "f.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", "1", "-i", str(path), "-frames:v", "1", str(out)], check=True)
        return Image.open(out).copy()


def main():
    sheets, drive = get_services()
    folder_id = get_or_create_folder(drive, "Mesa de Posteos/thumbs")
    since = (date.today() - timedelta(days=7)).isoformat()
    done = failed = 0

    targets = [(APPROVAL_SHEET_ID, f"'{tab}'!", tab, APPROVAL_COLS, False) for tab in APPROVAL_TABS]
    targets += [(c["sheet_id"], "", name, c, True) for name, c in CALENDARS.items()]

    for sheet_id, prefix, name, c, is_calendar in targets:
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=f"{prefix}A1:Z2000").execute().get("values", [])
        if not rows:
            continue
        rows = [r + [""] * (26 - len(r)) for r in rows]
        thumb = col_letter(c["thumb"])
        updates = [] if rows[0][c["thumb"]] else [{"range": f"{prefix}{thumb}1", "values": [["Thumb"]]}]

        for i, row in enumerate(rows[1:], start=2):
            media = row[c["media"]].strip()
            if row[c["status"]].strip().lower() not in WANTED or row[c["thumb"]] or not media:
                continue
            if is_calendar and row[c["date"]] < since:
                continue
            try:
                img = load_image(media).convert("RGB")
                img.thumbnail((480, 480))
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=80)
                buf.seek(0)
                f = drive.files().create(
                    body={"name": f"{name}-row{i}.jpg", "parents": [folder_id]},
                    media_body=MediaIoBaseUpload(buf, mimetype="image/jpeg"),
                    fields="id",
                ).execute()
                updates.append({"range": f"{prefix}{thumb}{i}", "values": [[f["id"]]]})
                done += 1
            except Exception as e:  # expired CDN link, missing local file, no ffmpeg — skip the row
                print(f"  {name} fila {i}: sin miniatura ({e.__class__.__name__}: {str(e)[:80]})")
                failed += 1

        if updates:
            sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id, body={"valueInputOption": "RAW", "data": updates}
            ).execute()

    print(f"{done} miniatura(s) nuevas, {failed} fallida(s).")


if __name__ == "__main__":
    main()
