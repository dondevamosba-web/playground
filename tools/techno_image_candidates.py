#!/usr/bin/env python3
"""
Propose VALIDATED image candidates for Techno rows without media, instead of
blind-filling like techno_fill_images did (which produced pool floats and
dehumidifiers). Candidates go to column L; nothing publishes until Guido taps
"Usar esta imagen" in the preview (approval_server copies L → I).

Validation: downloads the image, requires real decodable image, >= 80 KB,
>= 500px on the short side, and not Best Buy's 'Image Unavailable' placeholder.
Valid candidates are re-uploaded to Drive (public) so IG can always fetch them.

Runs Wed 9:10 via launchd, after queue-health refills.
"""
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from techno_fix_all_images import IMAGES as IMAGE_POOL

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
PLACEHOLDER_SIZES = {14867}  # Best Buy "Image Unavailable"


def validate(url):
    """Download and sanity-check; return image bytes or None."""
    try:
        r = requests.get(url, timeout=15, headers=UA)
        r.raise_for_status()
        raw = r.content
        if len(raw) < 80_000 or len(raw) in PLACEHOLDER_SIZES:
            return None
        img = Image.open(io.BytesIO(raw))
        img.load()
        if min(img.size) < 500:
            return None
        return raw
    except Exception:
        return None


def upload(drive, raw, name):
    from googleapiclient.http import MediaIoBaseUpload
    media = MediaIoBaseUpload(io.BytesIO(raw), mimetype="image/jpeg")
    f = drive.files().create(body={"name": f"techno_cand_{name}.jpg"},
                             media_body=media, fields="id").execute()
    drive.permissions().create(fileId=f["id"],
                               body={"role": "reader", "type": "anyone"}).execute()
    return f"https://drive.google.com/uc?export=download&id={f['id']}"


def main():
    sheets, drive = get_services()
    sid = os.environ["TECHNO_CONTENT_CALENDAR_SHEET_ID"]
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="A2:L1000").execute().get("values", [])
    updates = []
    for i, r in enumerate(rows, start=2):
        g = lambda j: r[j].strip() if len(r) > j else ""
        if g(9) != "pending" or g(8) or g(11) or not g(3):
            continue  # needs: pending, no media, no candidate yet, has product
        product = g(3)
        raw, chosen = None, ""
        for key in sorted(IMAGE_POOL, key=len, reverse=True):
            if key.lower() in product.lower():
                for url in IMAGE_POOL[key]:
                    if "bbystatic" in url:
                        continue  # known to serve wrong products
                    raw = validate(url)
                    if raw:
                        chosen = url
                        break
                break
        if not raw:
            print(f"fila {i}: {product[:40]} — sin candidata válida")
            continue
        cand = upload(drive, raw, product[:25].replace(" ", "_"))
        updates.append({"range": f"L{i}", "values": [[cand]]})
        print(f"fila {i}: {product[:40]} → candidata validada ({chosen[:45]})")
    if updates:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=sid, body={"valueInputOption": "RAW", "data": updates}).execute()
        print(f"{len(updates)} candidatas cargadas en col L")
    else:
        print("sin filas para proponer")


if __name__ == "__main__":
    main()
