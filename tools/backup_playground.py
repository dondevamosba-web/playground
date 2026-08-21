#!/usr/bin/env python3
"""Zip the playground repo (minus .git/.tmp/node_modules) and upload to Drive folder Backups/playground."""
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from upload_to_drive import get_drive_service, get_or_create_folder

from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".tmp", "node_modules", "__pycache__", ".venv", "venv"}
KEEP_BACKUPS = 4  # rotate: keep newest N in Drive


def make_zip() -> Path:
    out = Path("/tmp") / f"playground-backup-{datetime.now():%Y%m%d}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in ROOT.rglob("*"):
            rel = p.relative_to(ROOT)
            if p.is_dir() or any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if p.suffix == ".zip":
                continue
            zf.write(p, rel)
    return out


def rotate(service, folder_id: str):
    res = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        orderBy="createdTime desc", fields="files(id,name)",
    ).execute()
    for f in res.get("files", [])[KEEP_BACKUPS:]:
        service.files().delete(fileId=f["id"]).execute()
        print(f"Rotated out old backup: {f['name']}")


def main():
    zip_path = make_zip()
    size_mb = zip_path.stat().st_size / 1e6
    print(f"Created {zip_path} ({size_mb:.0f} MB)")
    service = get_drive_service()
    folder_id = get_or_create_folder(service, "Backups/playground")
    media = MediaFileUpload(str(zip_path), mimetype="application/zip", resumable=True)
    f = service.files().create(
        body={"name": zip_path.name, "parents": [folder_id]},
        media_body=media, fields="id,name",
    ).execute()
    print(f"Uploaded to Drive: {f['name']} (id {f['id']})")
    rotate(service, folder_id)
    zip_path.unlink()


if __name__ == "__main__":
    main()
