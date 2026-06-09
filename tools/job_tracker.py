#!/usr/bin/env python3
"""
Job application tracker.

Unified pipeline view across all job applications — whether they came from
job_cycle.py (cycle_log.json) or generate_email_drafts.py (email_drafts.json).

Syncs to the "Jobs" tab of the Outreach Tracker sheet, lets you update statuses
from the CLI, and surfaces stale applications that need a follow-up.

Status lifecycle:
  Drafted → Sent → Replied → Interview Scheduled → Offer | Rejected | Ghosted

Commands:
  sync      — pull both JSON files, add new entries to the Jobs sheet tab
  status    — pipeline overview grouped by status, with aging
  mark      — update an application's status from the CLI
  followups — list Sent apps with no reply for N+ days

Usage:
  python3 tools/job_tracker.py sync
  python3 tools/job_tracker.py status
  python3 tools/job_tracker.py status --all       # include Closed/Rejected/Ghosted
  python3 tools/job_tracker.py mark --company "STAPHAUS" --as Sent
  python3 tools/job_tracker.py mark --company "STAPHAUS" --as Replied --notes "HR reached out"
  python3 tools/job_tracker.py followups           # default 5 days
  python3 tools/job_tracker.py followups --days 7
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.outreach_tracker import OutreachTracker, HEADERS

TMP          = ROOT / ".tmp"
CYCLE_LOG    = TMP / "cycle_log.json"
DRAFTS_JSON  = TMP / "email_drafts.json"

VALID_STATUSES = {
    "drafted", "sent", "replied",
    "interview scheduled", "offer", "rejected", "ghosted",
}

# Column indices for Jobs tab (matches outreach_tracker.py)
C_COMPANY  = 0; C_TITLE = 1; C_LOCATION = 2; C_URL = 3
C_EMAIL    = 4; C_SUBJECT = 5; C_STATUS = 6; C_DATE = 7
C_FOLLOWUP = 8; C_NOTES = 9

TERMINAL_STATUSES = {"offer", "rejected", "ghosted"}


# ── Load local JSON sources ───────────────────────────────────────────────────

def load_cycle_log() -> list:
    if not CYCLE_LOG.exists():
        return []
    data = json.loads(CYCLE_LOG.read_text())
    rows = []
    for d in data:
        rows.append({
            "company":   d.get("company", ""),
            "title":     d.get("title", ""),
            "location":  d.get("location", ""),
            "url":       d.get("url", ""),
            "subject":   d.get("subject", ""),
            "date":      d.get("date_posted", date.today().isoformat()),
        })
    return rows


def load_email_drafts() -> list:
    if not DRAFTS_JSON.exists():
        return []
    data = json.loads(DRAFTS_JSON.read_text())
    rows = []
    for d in data:
        rows.append({
            "company":   d.get("company", ""),
            "title":     d.get("job_title", ""),
            "location":  d.get("location", ""),
            "url":       d.get("job_url", ""),
            "subject":   d.get("subject", ""),
            "date":      date.today().isoformat(),
        })
    return rows


# ── Sheet helpers ─────────────────────────────────────────────────────────────

def _read_jobs(tracker: OutreachTracker) -> list:
    return tracker._read_tab("Jobs")


def _get(row, col):
    return row[col].strip() if len(row) > col else ""


def _find_rows(all_rows: list, company: str) -> list:
    """Return (sheet_row_number, row) for rows matching company (1-based, skips header)."""
    matches = []
    for i, row in enumerate(all_rows[1:], start=2):
        if company.lower() in _get(row, C_COMPANY).lower():
            matches.append((i, row))
    return matches


def _update_cell(tracker: OutreachTracker, row_index: int, col: int, value: str):
    col_letter = chr(ord("A") + col)
    tracker.sheets.spreadsheets().values().update(
        spreadsheetId=tracker.sheet_id,
        range=f"Jobs!{col_letter}{row_index}",
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]},
    ).execute()


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_sync(tracker: OutreachTracker):
    sources = load_cycle_log() + load_email_drafts()
    if not sources:
        print("No local JSON files found. Run job_cycle.py or generate_email_drafts.py first.")
        return

    today = date.today().isoformat()
    rows = [
        [
            s["company"],
            s["title"],
            s["location"],
            s["url"],
            "",           # Email To (blank — it's a draft to yourself)
            s["subject"],
            "Drafted",
            s["date"] or today,
            "",           # Follow-up Date
            "",           # Notes
        ]
        for s in sources
        if s["url"]  # require URL as dedup key
    ]

    added = tracker.add_rows("Jobs", rows)
    total = len(sources)
    skipped = total - added
    print(f"Sync complete: {added} new application(s) added, {skipped} already in sheet.")
    print(f"Sheet: {tracker.url()}")


def cmd_status(tracker: OutreachTracker, show_all: bool):
    rows = _read_jobs(tracker)
    if len(rows) <= 1:
        print("No applications in tracker. Run `sync` first.")
        return

    today = date.today()
    buckets: dict[str, list] = {}
    for row in rows[1:]:
        status = _get(row, C_STATUS) or "Drafted"
        if not show_all and status.lower() in TERMINAL_STATUSES:
            continue
        buckets.setdefault(status, []).append(row)

    # Order
    order = ["Drafted", "Sent", "Replied", "Interview Scheduled",
             "Offer", "Rejected", "Ghosted"]
    total_active = sum(len(v) for v in buckets.values())

    print(f"\nJob Application Pipeline  ({today})  —  {total_active} active")
    print("=" * 70)

    for status in order:
        apps = buckets.get(status, [])
        if not apps:
            continue
        print(f"\n  {status.upper()}  ({len(apps)})")
        print(f"  {'Company':<28} {'Title':<30} {'Days ago':>9}")
        print(f"  {'-'*28} {'-'*30} {'-'*9}")
        for row in apps:
            company   = _get(row, C_COMPANY)[:26]
            title     = _get(row, C_TITLE)[:28]
            date_str  = _get(row, C_DATE)
            days_ago  = ""
            if date_str:
                try:
                    delta = (today - date.fromisoformat(date_str)).days
                    days_ago = f"{delta}d ago"
                except ValueError:
                    pass
            print(f"  {company:<28} {title:<30} {days_ago:>9}")

    print(f"\nSheet: {tracker.url()}")


def cmd_mark(tracker: OutreachTracker, company: str, new_status: str, notes: str):
    if new_status.lower() not in VALID_STATUSES:
        print(f"Invalid status '{new_status}'. Valid: {', '.join(sorted(VALID_STATUSES))}")
        return

    rows = _read_jobs(tracker)
    matches = _find_rows(rows, company)
    if not matches:
        print(f"No application found matching '{company}'. Use `status` to see what's tracked.")
        return

    # Update most recent match
    row_index, row = matches[-1]
    status_display = new_status.title()
    _update_cell(tracker, row_index, C_STATUS, status_display)

    # Set follow-up date to +5 days when marking Sent
    if new_status.lower() == "sent":
        followup = (date.today() + timedelta(days=5)).isoformat()
        _update_cell(tracker, row_index, C_FOLLOWUP, followup)

    if notes:
        existing = _get(row, C_NOTES)
        new_notes = f"{existing}; {notes}".lstrip("; ")
        _update_cell(tracker, row_index, C_NOTES, new_notes)

    company_name = _get(row, C_COMPANY)
    title        = _get(row, C_TITLE)
    print(f"Updated: {company_name} — {title}")
    print(f"  Status → {status_display}")
    if new_status.lower() == "sent":
        print(f"  Follow-up date set: {followup}")
    print(f"Sheet: {tracker.url()}")


def cmd_followups(tracker: OutreachTracker, days: int):
    rows = _read_jobs(tracker)
    if len(rows) <= 1:
        print("No applications in tracker. Run `sync` first.")
        return

    today = date.today()
    cutoff = today - timedelta(days=days)
    due = []

    for row in rows[1:]:
        status = _get(row, C_STATUS).lower()
        if status != "sent":
            continue

        followup_str = _get(row, C_FOLLOWUP)
        date_str     = _get(row, C_DATE)
        is_due = False

        if followup_str:
            try:
                if date.fromisoformat(followup_str) <= today:
                    is_due = True
            except ValueError:
                pass
        if not is_due and date_str:
            try:
                if date.fromisoformat(date_str) <= cutoff:
                    is_due = True
            except ValueError:
                pass

        if is_due:
            due.append(row)

    if not due:
        print(f"No follow-ups due (threshold: {days} days). All sent apps are within window.")
        return

    print(f"\nFollow-ups due  (>{days}d since sent, no reply)  —  {len(due)} application(s)")
    print("=" * 70)
    for row in due:
        company  = _get(row, C_COMPANY)
        title    = _get(row, C_TITLE)
        date_str = _get(row, C_DATE)
        email    = _get(row, C_EMAIL)
        url      = _get(row, C_URL)
        print(f"\n  {company} — {title}")
        if date_str:
            try:
                delta = (today - date.fromisoformat(date_str)).days
                print(f"  Applied {delta} days ago ({date_str})")
            except ValueError:
                print(f"  Applied: {date_str}")
        if email:
            print(f"  Email: {email}")
        if url:
            print(f"  {url}")
        print(f"  → Run: python3 tools/job_tracker.py mark --company \"{company}\" --as Replied")

    print(f"\nSheet: {tracker.url()}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="job_tracker")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("sync", help="Sync cycle_log.json + email_drafts.json to sheet")

    p_status = sub.add_parser("status", help="Pipeline overview by status")
    p_status.add_argument("--all", action="store_true", help="Include Offer/Rejected/Ghosted")

    p_mark = sub.add_parser("mark", help="Update an application's status")
    p_mark.add_argument("--company", required=True)
    p_mark.add_argument("--as",      required=True, dest="new_status",
                        help="New status: drafted | sent | replied | interview scheduled | offer | rejected | ghosted")
    p_mark.add_argument("--notes",   default="")

    p_fu = sub.add_parser("followups", help="List stale sent applications")
    p_fu.add_argument("--days", type=int, default=5)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    tracker = OutreachTracker()

    if args.cmd == "sync":
        cmd_sync(tracker)
    elif args.cmd == "status":
        cmd_status(tracker, show_all=args.all)
    elif args.cmd == "mark":
        cmd_mark(tracker, args.company, args.new_status, args.notes)
    elif args.cmd == "followups":
        cmd_followups(tracker, args.days)


if __name__ == "__main__":
    main()
