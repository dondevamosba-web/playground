#!/usr/bin/env python3
"""
Queue health check + auto-refill.

Counts future unposted rows per account calendar. If an account has fewer
than MIN_QUEUE, runs its fill_content_* script (new rows land as "pending",
so nothing publishes without approval — they show up in the morning preview).

Runs weekly (Wed 9:00) via launchd; --check-only to just report.

Usage:
  python3 tools/queue_health.py [--check-only]
"""
import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

MIN_QUEUE = 25   # publish-one-each drena 3/día desde 2026-07-07; 25 ≈ 8 días
FILL_WEEKS = 3

# account: (sheet env, status col idx, fill script or None)
ACCOUNTS = {
    "Ola Digital": ("CONTENT_CALENDAR_SHEET_ID", 8, "fill_content_calendar.py"),
    "Storm":       ("STORM_CONTENT_CALENDAR_SHEET_ID", 8, "fill_content_storm.py"),
    "Techno":      ("TECHNO_CONTENT_CALENDAR_SHEET_ID", 9, "fill_content_techno.py"),
    "Empleo":      ("OLA_EMPLEO_CALENDAR_SHEET_ID", 8, "fill_content_ola_empleo.py"),
    "Talento USA": ("TALENTO_USA_CALENDAR_SHEET_ID", 8, "fill_content_talento_usa.py"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()

    sheets, _ = get_services()
    today = str(date.today())
    for acct, (env, st_col, fill) in ACCOUNTS.items():
        sid = os.getenv(env)
        if not sid:
            continue
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=sid, range="A2:K1000").execute().get("values", [])
        future = sum(
            1 for r in rows
            if len(r) > st_col and r[st_col].strip() in ("pending", "approved")
            and (len(r) <= st_col + 1 or not r[st_col + 1].strip())
            and r[0][:10] >= today)
        low = future < MIN_QUEUE
        print(f"{acct}: {future} posts futuros en cola" + (" — BAJA" if low else ""))
        if low and not a.check_only and fill:
            print(f"  → rellenando con {fill} --weeks {FILL_WEEKS}")
            r = subprocess.run([sys.executable, str(ROOT / "tools" / fill),
                                "--weeks", str(FILL_WEEKS)],
                               capture_output=True, text=True, cwd=str(ROOT))
            tail = (r.stdout + r.stderr).strip().splitlines()[-2:]
            for ln in tail:
                print(f"    {ln}")
            if r.returncode != 0:
                print(f"    ERROR exit {r.returncode}")


if __name__ == "__main__":
    main()
