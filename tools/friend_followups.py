#!/usr/bin/env python3
"""
Friend follow-up reminder: reads "Friend Follow-ups" Google Sheet,
finds friends who are overdue for a message, and drafts a reminder
email to dondevamosba@gmail.com.

Usage:
  python3 tools/friend_followups.py             # check and create draft reminders
  python3 tools/friend_followups.py --dry-run   # check only, no drafts
  python3 tools/friend_followups.py --setup     # create sheet and add example row
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.sheets_client import get_services
from tools.gmail_draft import create_draft

SHEET_NAME = "Friend Follow-ups"
REMINDER_TO = "dondevamosba@gmail.com"
HEADERS = ["Name", "Last Contact", "Frequency (days)", "Notes"]
# Column indices (0-based)
COL_NAME      = 0
COL_LAST      = 1
COL_FREQ      = 2
COL_NOTES     = 3


class FriendTracker:
    def __init__(self):
        self.sheets, self.drive = get_services()
        self.sheet_id = self._find_or_create()

    def url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"

    def _find_or_create(self):
        q = (f"name='{SHEET_NAME}' and "
             "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false")
        files = self.drive.files().list(q=q, fields="files(id)").execute().get("files", [])
        if files:
            return files[0]["id"]

        body = {"properties": {"title": SHEET_NAME}}
        sheet_id = self.sheets.spreadsheets().create(
            body=body, fields="spreadsheetId"
        ).execute()["spreadsheetId"]
        self.drive.permissions().create(
            fileId=sheet_id, body={"type": "anyone", "role": "writer"}
        ).execute()
        # Write headers — use first sheet's actual title
        meta = self.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
        tab_title = meta["sheets"][0]["properties"]["title"]
        self.sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{tab_title}'!A1",
            valueInputOption="RAW",
            body={"values": [HEADERS]},
        ).execute()
        print(f"Created sheet: {SHEET_NAME}")
        return sheet_id

    def _tab(self):
        meta = self.sheets.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
        return meta["sheets"][0]["properties"]["title"]

    def add_friend(self, name: str, last_contact: str, frequency_days: int, notes: str = ""):
        self.sheets.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=f"'{self._tab()}'!A1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [[name, last_contact, frequency_days, notes]]},
        ).execute()
        print(f"Added: {name}")

    def get_overdue(self) -> list[dict]:
        result = self.sheets.spreadsheets().values().get(
            spreadsheetId=self.sheet_id,
            range=f"'{self._tab()}'!A1:Z",
        ).execute()
        rows = result.get("values", [])
        if len(rows) < 2:
            return []

        today = date.today()
        overdue = []
        for row in rows[1:]:  # skip header
            if len(row) < 3:
                continue
            name = row[COL_NAME].strip()
            last_str = row[COL_LAST].strip()
            freq_str = row[COL_FREQ].strip()
            notes = row[COL_NOTES].strip() if len(row) > COL_NOTES else ""

            try:
                last = date.fromisoformat(last_str)
                freq = int(freq_str)
            except ValueError:
                continue

            due = last + timedelta(days=freq)
            if today >= due:
                overdue.append({
                    "name": name,
                    "last_contact": last_str,
                    "frequency": freq,
                    "due": due.isoformat(),
                    "days_overdue": (today - due).days,
                    "notes": notes,
                })
        return overdue


def main():
    dry_run = "--dry-run" in sys.argv
    setup = "--setup" in sys.argv

    tracker = FriendTracker()

    if setup:
        tracker.add_friend("Severiano", "2025-04-01", 30, "Catch up, check how things are going")
        print(f"Sheet: {tracker.url()}")
        return

    overdue = tracker.get_overdue()

    if not overdue:
        print("No friends overdue. All caught up.")
        print(f"Sheet: {tracker.url()}")
        return

    print(f"{len(overdue)} friend(s) to reach out to:\n")
    drafts = 0

    for f in overdue:
        label = f"  {f['name']} — last contact {f['last_contact']}"
        if f["days_overdue"] > 0:
            label += f" ({f['days_overdue']}d overdue)"
        else:
            label += " (due today)"
        if f["notes"]:
            label += f"\n    Notes: {f['notes']}"
        print(label)

        if not dry_run:
            subject = f"Reminder: send {f['name']} a message"
            lines = [f"Hey, it's time to reach out to {f['name']}."]
            if f["notes"]:
                lines.append(f"Notes: {f['notes']}")
            lines.append(f"Last contact: {f['last_contact']} (every {f['frequency']} days)")
            body = "\n\n".join(lines)
            try:
                result = create_draft(to=REMINDER_TO, subject=subject, body=body)
                print(f"    → Draft created ({result['draft_id']})")
                drafts += 1
            except Exception as e:
                print(f"    → Failed: {e}")

    if not dry_run:
        print(f"\n{drafts} reminder draft(s) created → {REMINDER_TO}")
    print(f"Sheet: {tracker.url()}")


if __name__ == "__main__":
    main()
