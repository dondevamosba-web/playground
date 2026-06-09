#!/usr/bin/env python3
"""One-time setup: create the expense log Google Sheet and share with service account."""
import json
from pathlib import Path
from dotenv import load_dotenv, set_key

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

from sheets_client import get_services

SA_EMAIL = "expense-logger@ola-digital-496915.iam.gserviceaccount.com"
HEADERS  = [["Timestamp","Month","Type","Day","Description","ARS","USD","Category","Payment","Status"]]

def main():
    sheets, drive = get_services()

    # Create spreadsheet
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": "💸 Gastos Log"},
        "sheets": [{"properties": {"title": "Log"}}]
    }, fields="spreadsheetId").execute()
    sheet_id = spreadsheet["spreadsheetId"]
    print(f"Created sheet: {sheet_id}")

    # Add headers
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="Log!A1",
        valueInputOption="RAW",
        body={"values": HEADERS}
    ).execute()

    # Share with service account
    drive.permissions().create(
        fileId=sheet_id,
        body={"type": "user", "role": "writer", "emailAddress": SA_EMAIL},
        sendNotificationEmail=False,
    ).execute()
    print(f"Shared with {SA_EMAIL}")

    # Save to .env
    set_key(str(ROOT / ".env"), "EXPENSE_SHEET_ID", sheet_id)
    print(f"\n✅ Done! Sheet ID saved to .env")
    print(f"   Open: https://docs.google.com/spreadsheets/d/{sheet_id}")

if __name__ == "__main__":
    main()
