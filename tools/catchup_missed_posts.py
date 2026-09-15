#!/usr/bin/env python3
"""
Catch-up for posts missed while the Mac was off/asleep.

Scans the unified approval sheet's Fiestas tab for approved rows whose
Schedule Date fell out of the 24h publish window without being posted:
  - event still in the future (via the Fiestas Queue sheet, matched by name)
    → reschedule to the next publisher slot, still before the event
  - event already happened → mark "expired"
  - event date unknown → mark "review" (never auto-post stale content blind)

The 5 calendar accounts need no catch-up: publish_one_each already posts
oldest-first, so their backlog drains on its own.

Runs at Mac boot (RunAtLoad) and daily 8:10 via launchd.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT_AR = timezone(timedelta(hours=-3))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from tools.sheets_client import get_services

SLOT_HOURS = [13, 15, 17, 19, 21]  # publish-approved run hours (AR)


def next_slot(now, event_date):
    """Next publisher slot >= now that is still before the event day ends."""
    for day_off in range(0, 3):
        day = (now + timedelta(days=day_off)).date()
        if str(day) > event_date:
            break
        for h in SLOT_HOURS:
            slot = datetime(day.year, day.month, day.day, h, 0, tzinfo=ROOT_AR)
            if slot >= now:
                return f"{day} {h:02d}:00"
    return None


def main():
    now = datetime.now(ROOT_AR)
    today = now.strftime("%Y-%m-%d")
    sheets, _ = get_services()
    uid = os.environ["UNIFIED_APPROVAL_SHEET_ID"]
    fid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]

    # name[:40] -> event date, from the Queue sheet
    qrows = sheets.spreadsheets().values().get(
        spreadsheetId=fid, range="Queue!A2:M500").execute().get("values", [])
    ev_dates = {}
    for r in qrows:
        if len(r) > 3 and r[2].strip() and r[3].strip():
            ev_dates[r[2].strip()[:40].lower()] = r[3].strip()

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=uid, range="'Fiestas'!A2:G300").execute().get("values", [])
    updates = []
    for i, r in enumerate(rows, start=2):
        g = lambda j: r[j].strip() if len(r) > j else ""
        if g(4).lower() != "approved" or g(6):
            continue
        try:
            sched = datetime.strptime(g(3), "%Y-%m-%d %H:%M").replace(tzinfo=ROOT_AR)
        except ValueError:
            continue
        if now - sched <= timedelta(hours=24):
            continue  # still inside the publisher's own window
        name = g(5)[:40].lower()
        ev = ev_dates.get(name, "")
        if ev and ev >= today:
            slot = next_slot(now, ev)
            if slot:
                updates.append({"range": f"'Fiestas'!D{i}", "values": [[slot]]})
                print(f"fila {i}: {g(5)[:40]} (evento {ev}) reprogramado → {slot}")
                continue
        status = "expired" if ev else "review"
        updates.append({"range": f"'Fiestas'!E{i}", "values": [[status]]})
        print(f"fila {i}: {g(5)[:40]} → {status}" + (f" (evento {ev} ya pasó)" if ev else " (fecha de evento desconocida)"))

    if updates:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=uid, body={"valueInputOption": "RAW", "data": updates}).execute()
        print(f"{len(updates)} filas actualizadas")
    else:
        print("nada perdido — todo al día")


if __name__ == "__main__":
    main()
