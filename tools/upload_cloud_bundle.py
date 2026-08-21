#!/usr/bin/env python3
"""
Bundle the publishing toolchain + credentials into a zip and upload it to
Drive under a STABLE file id, so the cloud publisher routine can bootstrap.

Includes: tools/*.py, tools/*.json, .env, credentials.json, token_sheets.json,
requirements.txt. Excludes __pycache__ and anything else.

Run after changing any publishing tool so the cloud copy stays current:
  python3 tools/upload_cloud_bundle.py
"""
import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from googleapiclient.http import MediaIoBaseUpload
from tools.sheets_client import get_services

BUNDLE_NAME = "playground-cloud-publisher.zip"


def build_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for pat in ("tools/*.py", "tools/*.json"):
            for p in ROOT.glob(pat):
                zf.write(p, p.relative_to(ROOT))
        for name in (".env", "credentials.json", "token_sheets.json", "requirements.txt"):
            p = ROOT / name
            if p.exists():
                zf.write(p, name)
    return buf.getvalue()


def main():
    data = build_zip()
    _, drive = get_services()
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="application/zip")
    hits = drive.files().list(
        q=f"name = '{BUNDLE_NAME}' and trashed = false",
        fields="files(id)").execute().get("files", [])
    if hits:
        fid = hits[0]["id"]
        drive.files().update(fileId=fid, media_body=media).execute()
        action = "actualizado"
    else:
        f = drive.files().create(
            body={"name": BUNDLE_NAME}, media_body=media, fields="id").execute()
        fid = f["id"]
        action = "creado"
    print(f"{action}: {BUNDLE_NAME} ({len(data)/1e6:.1f} MB) — file id: {fid}")


if __name__ == "__main__":
    main()
