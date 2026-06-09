#!/usr/bin/env python3
"""
Upload images from a local folder to Google Drive and return public URLs.
Used to bridge Canva exports → Instagram-ready public URLs.

Setup (one-time):
  1. Go to console.cloud.google.com
  2. Create/select a project → Enable "Google Drive API"
  3. Create OAuth 2.0 credentials (Desktop app) → Download as credentials.json
  4. Place credentials.json in the project root
  5. Run this script once — browser will open for auth, then token.json is saved

Usage:
  python tools/upload_to_drive.py --folder .tmp/posts/
  python tools/upload_to_drive.py --files .tmp/posts/post1.png .tmp/posts/post2.png
  python tools/upload_to_drive.py --folder .tmp/posts/ --drive-folder "Ola Digital/Instagram"
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / "token.json"

SUPPORTED_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}


def get_drive_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("ERROR: credentials.json not found in project root.")
                print("See workflows/upload_to_drive.md or tools/upload_to_drive.py docstring for setup.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())
        print(f"Auth saved to {TOKEN_FILE}")

    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, folder_path: str) -> str:
    """Create nested folders if needed, return the final folder ID."""
    parts = [p for p in folder_path.strip("/").split("/") if p]
    parent_id = "root"

    for part in parts:
        query = (
            f"name='{part}' and mimeType='application/vnd.google-apps.folder' "
            f"and '{parent_id}' in parents and trashed=false"
        )
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])

        if files:
            parent_id = files[0]["id"]
        else:
            metadata = {
                "name": part,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_id],
            }
            folder = service.files().create(body=metadata, fields="id").execute()
            parent_id = folder["id"]
            print(f"  Created folder: {part}")

    return parent_id


def make_public(service, file_id: str):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()


def get_public_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def upload_file(service, local_path: Path, parent_id: str) -> dict:
    suffix = local_path.suffix.lower()
    mime_type = SUPPORTED_TYPES.get(suffix)
    if not mime_type:
        print(f"  Skipping {local_path.name} — unsupported type ({suffix})")
        return None

    print(f"  Uploading {local_path.name}...")
    metadata = {"name": local_path.name, "parents": [parent_id]}
    media = MediaFileUpload(str(local_path), mimetype=mime_type, resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields="id,name").execute()

    make_public(service, file["id"])
    url = get_public_url(file["id"])
    return {"name": file["name"], "id": file["id"], "url": url}


def main():
    parser = argparse.ArgumentParser(description="Upload images to Google Drive and return public URLs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--folder", help="Local folder containing images to upload")
    group.add_argument("--files", nargs="+", help="Specific local files to upload")
    parser.add_argument("--drive-folder", default="Ola Digital/Instagram Posts", help="Drive folder path (default: Ola Digital/Instagram Posts)")
    parser.add_argument("--output", help="Save results as JSON to this path")
    args = parser.parse_args()

    service = get_drive_service()
    print(f"Uploading to Drive folder: {args.drive_folder}")
    folder_id = get_or_create_folder(service, args.drive_folder)

    files_to_upload = []
    if args.folder:
        folder = Path(args.folder)
        if not folder.exists():
            print(f"ERROR: Folder not found: {folder}")
            sys.exit(1)
        files_to_upload = sorted([f for f in folder.iterdir() if f.is_file()])
    else:
        files_to_upload = [Path(f) for f in args.files]

    results = []
    for f in files_to_upload:
        result = upload_file(service, f, folder_id)
        if result:
            results.append(result)
            print(f"    URL: {result['url']}")

    print(f"\nUploaded {len(results)} file(s).")

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2))
        print(f"Results saved to {args.output}")
    else:
        print("\nPublic URLs:")
        for r in results:
            print(f"  {r['name']}: {r['url']}")


if __name__ == "__main__":
    main()
