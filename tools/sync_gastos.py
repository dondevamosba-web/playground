#!/usr/bin/env python3
"""
Full sync: import Netlify form submissions → rebuild Excel → upload to Google Drive.

Usage:
    python tools/sync_gastos.py          # full sync
    python tools/sync_gastos.py --build-only   # skip Netlify import
    python tools/sync_gastos.py --upload-only  # skip rebuild, just re-upload

The Drive file ID is stored in .env as GASTOS_DRIVE_FILE_ID after the first upload.
Open the printed link in a browser → Google Sheets can open it online.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

from dotenv import load_dotenv, set_key
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT          = Path(__file__).parent.parent
XLSX_PATH     = ROOT / "Gastos_Final.xlsx"
CREDENTIALS   = ROOT / "credentials.json"
TOKEN_FILE    = ROOT / "token_sheets.json"
ENV_FILE      = ROOT / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_drive_service():
    load_dotenv(ENV_FILE)
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds)


def upload_or_replace(service, file_id=None):
    media = MediaFileUpload(str(XLSX_PATH), mimetype=XLSX_MIME, resumable=True)

    if file_id:
        print(f"  Replacing existing Drive file ({file_id})...")
        result = service.files().update(
            fileId=file_id,
            media_body=media,
            fields="id,name,webViewLink",
        ).execute()
    else:
        print("  Uploading new file to Google Drive...")
        metadata = {"name": "Gastos_Final.xlsx"}
        result = service.files().create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink",
        ).execute()
        # Save the file ID to .env so future runs replace the same file
        set_key(str(ENV_FILE), "GASTOS_DRIVE_FILE_ID", result["id"])
        print(f"  Saved file ID to .env → GASTOS_DRIVE_FILE_ID={result['id']}")

    return result


def run(cmd, desc):
    print(f"\n{'─'*50}")
    print(f"▶ {desc}")
    print('─'*50)
    result = subprocess.run(cmd, shell=True, executable="/bin/zsh")
    if result.returncode != 0:
        print(f"\n✗ Failed: {desc}")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-only",  action="store_true")
    parser.add_argument("--upload-only", action="store_true")
    args = parser.parse_args()

    load_dotenv(ENV_FILE)

    if not args.upload_only:
        run("python3 tools/import_netlify_forms.py", "Importing Netlify form submissions")
        run("python3 tools/build_gastos_final.py",   "Rebuilding Gastos_Final.xlsx")

    if not args.build_only:
        if not XLSX_PATH.exists():
            print(f"ERROR: {XLSX_PATH} not found. Run without --upload-only first.")
            sys.exit(1)

        print(f"\n{'─'*50}")
        print("▶ Uploading to Google Drive")
        print('─'*50)

        file_id = os.getenv("GASTOS_DRIVE_FILE_ID") or None
        service = get_drive_service()
        result  = upload_or_replace(service, file_id)

        link = result.get("webViewLink", f"https://drive.google.com/file/d/{result['id']}/view")
        print(f"\n✅ Done!")
        print(f"   Google Drive link: {link}")
        print(f"\n   Tip: open the link → click 'Open with Google Sheets' to view/edit online")


if __name__ == "__main__":
    main()
