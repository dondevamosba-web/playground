"""
Unified "Outreach Tracker" Google Sheet with tabs: Jobs, Roofing, HVAC.

Usage:
    from tools.outreach_tracker import OutreachTracker
    tracker = OutreachTracker()
    tracker.add_rows("Roofing", [["Acme Roofing", "Dallas", "joe@acme.com", ...]])
    overdue = tracker.get_overdue("Roofing", days=5)
    print(tracker.url())
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.sheets_client import get_services

SHEET_NAME = "Outreach Tracker"
TABS = ["Jobs", "Roofing", "HVAC", "Plumbing"]

HEADERS = {
    "Jobs": [
        "Company", "Job Title", "Location", "Job URL",
        "Email To", "Subject", "Status", "Date Added", "Follow-up Date", "Notes",
    ],
    "Roofing": [
        "Company", "City", "Email", "Phone", "Website",
        "Rating", "FB Ads Status", "Status", "Date Sent", "Follow-up Date", "Notes", "Variant",
    ],
    "HVAC": [
        "Company", "City", "Email", "Phone", "Website",
        "Rating", "FB Ads Status", "Status", "Date Sent", "Follow-up Date", "Notes", "Variant",
    ],
    "Plumbing": [
        "Company", "City", "Email", "Phone", "Website",
        "Rating", "FB Ads Status", "Status", "Date Sent", "Follow-up Date", "Notes",
    ],
}

# 0-based column indices
DEDUP_COL    = {"Jobs": 3,  "Roofing": 2,  "HVAC": 2,  "Plumbing": 2}   # Job URL / Email
STATUS_COL   = {"Jobs": 6,  "Roofing": 7,  "HVAC": 7,  "Plumbing": 7}
DATE_COL     = {"Jobs": 7,  "Roofing": 8,  "HVAC": 8,  "Plumbing": 8}   # Date Added / Date Sent
FOLLOWUP_COL = {"Jobs": 8,  "Roofing": 9,  "HVAC": 9,  "Plumbing": 9}
VARIANT_COL  = {"Roofing": 11, "HVAC": 11}


class OutreachTracker:
    def __init__(self):
        self.sheets, self.drive = get_services()
        self.sheet_id = self._find_or_create()

    def url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"

    # ── setup ─────────────────────────────────────────────────────────────────

    def _find_or_create(self):
        q = (f"name='{SHEET_NAME}' and "
             "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false")
        files = self.drive.files().list(q=q, fields="files(id)").execute().get("files", [])
        if files:
            sheet_id = files[0]["id"]
        else:
            body = {"properties": {"title": SHEET_NAME}}
            sheet_id = self.sheets.spreadsheets().create(
                body=body, fields="spreadsheetId"
            ).execute()["spreadsheetId"]
            self.drive.permissions().create(
                fileId=sheet_id, body={"type": "anyone", "role": "writer"}
            ).execute()
            print(f"Created sheet: {SHEET_NAME}")
        self._ensure_tabs(sheet_id)
        return sheet_id

    def _ensure_tabs(self, sheet_id):
        meta = self.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
        existing = {s["properties"]["title"] for s in meta["sheets"]}

        add_requests = [
            {"addSheet": {"properties": {"title": tab}}}
            for tab in TABS if tab not in existing
        ]
        if add_requests:
            self.sheets.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body={"requests": add_requests}
            ).execute()
            for req in add_requests:
                tab = req["addSheet"]["properties"]["title"]
                self._append(sheet_id, tab, [HEADERS[tab]])
                self._bold_freeze(sheet_id, tab)

        # Remove the default "Sheet1" if it was auto-created
        meta2 = self.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
        all_sheets = meta2["sheets"]
        default = next(
            (s for s in all_sheets if s["properties"]["title"] == "Sheet1"), None
        )
        if default and len(all_sheets) > 1:
            self.sheets.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={"requests": [{"deleteSheet": {"sheetId": default["properties"]["sheetId"]}}]},
            ).execute()

    def _bold_freeze(self, sheet_id, tab_name):
        meta = self.sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
        grid_id = next(
            s["properties"]["sheetId"]
            for s in meta["sheets"]
            if s["properties"]["title"] == tab_name
        )
        self.sheets.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": [
                {
                    "repeatCell": {
                        "range": {"sheetId": grid_id, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": grid_id,
                            "gridProperties": {"frozenRowCount": 1},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
            ]},
        ).execute()

    # ── read / write ──────────────────────────────────────────────────────────

    def _append(self, sheet_id, tab, rows):
        self.sheets.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{tab}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": rows},
        ).execute()

    def _read_tab(self, tab):
        result = self.sheets.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=f"{tab}!A:Z"
        ).execute()
        return result.get("values", [])

    def _existing_keys(self, tab):
        rows = self._read_tab(tab)
        if not rows:
            return set()
        col = DEDUP_COL[tab]
        return {row[col] for row in rows[1:] if len(row) > col and row[col]}

    # ── public API ────────────────────────────────────────────────────────────

    def add_rows(self, niche: str, rows: list) -> int:
        """Append rows to a niche tab, skipping duplicates by dedup key. Returns count added."""
        existing = self._existing_keys(niche)
        col = DEDUP_COL[niche]
        new = [r for r in rows if len(r) > col and r[col] not in existing]
        if new:
            self._append(self.sheet_id, niche, new)
        return len(new)

    def get_overdue(self, niche: str, days: int = 5) -> list:
        """
        Return rows where Status='Sent' and either:
          - Follow-up Date is set and <= today, OR
          - Date Sent/Added + days <= today
        Each row is returned as a dict keyed by column header.
        """
        rows = self._read_tab(niche)
        if len(rows) <= 1:
            return []

        today = date.today()
        cutoff = today - timedelta(days=days)
        headers = HEADERS[niche]
        s_col = STATUS_COL[niche]
        d_col = DATE_COL[niche]
        f_col = FOLLOWUP_COL[niche]

        overdue = []
        for row in rows[1:]:
            def get(idx):
                return row[idx].strip() if len(row) > idx else ""

            if get(s_col).lower() != "sent":
                continue

            due = False
            followup_str = get(f_col)
            if followup_str:
                try:
                    if date.fromisoformat(followup_str) <= today:
                        due = True
                except ValueError:
                    pass

            if not due:
                date_str = get(d_col)
                if date_str:
                    try:
                        if date.fromisoformat(date_str) <= cutoff:
                            due = True
                    except ValueError:
                        pass

            if due:
                overdue.append(
                    {headers[i]: (row[i].strip() if len(row) > i else "") for i in range(len(headers))}
                )

        return overdue

    def pipeline_summary(self) -> dict:
        """Return {niche: {status: count}} for all tabs."""
        summary = {}
        for tab in TABS:
            rows = self._read_tab(tab)
            s_col = STATUS_COL[tab]
            counts = {}
            for row in rows[1:]:
                s = row[s_col].strip() if len(row) > s_col else "Unknown"
                counts[s] = counts.get(s, 0) + 1
            summary[tab] = counts
        return summary

    def reply_rate_by_variant(self, niche: str) -> dict:
        """
        Return reply rate per variant for a niche tab.

        A row counts as "replied" if Status is Replied, Call Booked, or Closed.
        Returns {variant: {"sent": N, "replied": N, "rate": "X%"}}
        Rows with no Variant value are grouped under "unknown".
        """
        rows = self._read_tab(niche)
        if len(rows) <= 1 or niche not in VARIANT_COL:
            return {}

        s_col = STATUS_COL[niche]
        v_col = VARIANT_COL[niche]
        positive = {"replied", "call booked", "closed"}

        counts = {}
        for row in rows[1:]:
            variant = (row[v_col].strip() if len(row) > v_col else "") or "unknown"
            status = (row[s_col].strip().lower() if len(row) > s_col else "")
            if variant not in counts:
                counts[variant] = {"sent": 0, "replied": 0}
            counts[variant]["sent"] += 1
            if status in positive:
                counts[variant]["replied"] += 1

        for v, c in counts.items():
            rate = (c["replied"] / c["sent"] * 100) if c["sent"] else 0
            c["rate"] = f"{rate:.1f}%"

        return counts
