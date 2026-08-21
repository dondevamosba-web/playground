#!/usr/bin/env python3
"""
Build/refresh the "Calendario" tab in the unified approval sheet:
next 28 days as rows, one column per account, showing scheduled posts.
Empty cells (gaps) are highlighted red via conditional formatting.

Usage:
  python tools/build_unified_calendar.py [--days 28]
"""
import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ID = os.environ["UNIFIED_APPROVAL_SHEET_ID"]
ACCOUNTS = ["Ola Digital", "Storm", "Fiestas", "Techno", "Ola Empleo", "Talento USA"]
TAB = "Calendario"
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def parse_day(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:16] if "T" in fmt or " " in fmt else s[:10], fmt).date()
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    args = ap.parse_args()

    sheets, _ = get_services()
    meta = sheets.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    tabs = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}

    # collect scheduled posts per account/day
    today = date.today()
    horizon = today + timedelta(days=args.days)
    grid = {}  # (day, account) -> list of "status: caption…"
    for acct in ACCOUNTS:
        res = sheets.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"'{acct}'!A2:G").execute()
        for r in res.get("values", []):
            r = r + [""] * (7 - len(r))
            day = parse_day(r[3])
            if day and today <= day <= horizon and r[4] not in ("rejected",):
                snippet = (r[1] or "").replace("\n", " ")[:40]
                grid.setdefault((day, acct), []).append(f"[{r[4] or 'draft'}] {snippet}")

    # build values
    values = [["Fecha", "Día"] + ACCOUNTS]
    for i in range(args.days + 1):
        d = today + timedelta(days=i)
        row = [str(d), DIAS[d.weekday()]]
        row += ["\n".join(grid.get((d, a), [])) for a in ACCOUNTS]
        values.append(row)

    # (re)create tab
    reqs = []
    if TAB in tabs:
        reqs.append({"updateCells": {"range": {"sheetId": tabs[TAB]}, "fields": "userEnteredValue,userEnteredFormat"}})
    else:
        resp = sheets.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": TAB, "index": 0}}}]}).execute()
        tabs[TAB] = resp["replies"][0]["addSheet"]["properties"]["sheetId"]
    tid = tabs[TAB]

    if reqs:
        sheets.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": reqs}).execute()
    sheets.spreadsheets().values().update(
        spreadsheetId=SHEET_ID, range=f"{TAB}!A1", valueInputOption="RAW",
        body={"values": values}).execute()

    n = len(values)
    fmt_reqs = [
        {"repeatCell": {"range": {"sheetId": tid, "startRowIndex": 0, "endRowIndex": 1},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold"}},
        {"updateDimensionProperties": {"range": {"sheetId": tid, "dimension": "COLUMNS",
                                                 "startIndex": 2, "endIndex": 6},
                                       "properties": {"pixelSize": 220}, "fields": "pixelSize"}},
        # highlight gaps: blank account cells in red
        {"addConditionalFormatRule": {"rule": {
            "ranges": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": n,
                        "startColumnIndex": 2, "endColumnIndex": 6}],
            "booleanRule": {"condition": {"type": "BLANK"},
                            "format": {"backgroundColor": {"red": 1.0, "green": 0.85, "blue": 0.85}}}},
            "index": 0}},
    ]
    sheets.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={"requests": fmt_reqs}).execute()

    filled = len(grid)
    print(f"Calendario actualizado: {args.days + 1} días × {len(ACCOUNTS)} cuentas, {filled} celdas con posts")
    print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == "__main__":
    main()
