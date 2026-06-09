"""
Job application pipeline CRM — view and manage your job hunt funnel.

Commands:
  report      Print funnel summary by stage
  followups   List applications overdue for follow-up
  update      Update the status of a specific application
  add         Manually add an application (when applied outside job_cycle)
  open        Print the Google Sheet URL

Usage:
  python3 tools/job_pipeline.py report
  python3 tools/job_pipeline.py followups --days 4
  python3 tools/job_pipeline.py update --company "Acme" --status "Interview Scheduled"
  python3 tools/job_pipeline.py add --company "Stripe" --title "Growth Manager" --url "https://..."
  python3 tools/job_pipeline.py open
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.outreach_tracker import OutreachTracker
from tools.sheets_client import get_services

STAGES = ["Drafted", "Sent", "Replied", "Interview Scheduled", "Offer", "Rejected", "Ghosted"]
STAGE_EMOJI = {
    "Drafted":            "✏️ ",
    "Sent":               "📤",
    "Replied":            "💬",
    "Interview Scheduled":"📅",
    "Offer":              "🎉",
    "Rejected":           "❌",
    "Ghosted":            "👻",
}


def cmd_report(tracker: OutreachTracker):
    summary = tracker.pipeline_summary()
    jobs = summary.get("Jobs", {})

    print("\n── Job Application Funnel ────────────────────────────\n")
    total = sum(jobs.values())
    for stage in STAGES:
        count = jobs.get(stage, 0)
        bar = "█" * count
        emoji = STAGE_EMOJI.get(stage, "  ")
        print(f"  {emoji}  {stage:<22} {count:>3}  {bar}")

    # Also show any stages not in the standard list
    for stage, count in jobs.items():
        if stage not in STAGES and stage:
            print(f"       {stage:<22} {count:>3}")

    print(f"\n  Total tracked: {total}")
    print(f"\n  Sheet → {tracker.url()}\n")


def cmd_followups(tracker: OutreachTracker, days: int = 4):
    overdue = tracker.get_overdue("Jobs", days=days)
    if not overdue:
        print(f"\n  No follow-ups overdue (threshold: {days} days since sent).\n")
        return

    print(f"\n── Follow-ups Due ({len(overdue)} applications) ──────────────────\n")
    for r in overdue:
        company   = r.get("Company", "—")
        title     = r.get("Job Title", "—")
        date_sent = r.get("Date Added", "—")
        email     = r.get("Email To", "—")
        url       = r.get("Job URL", "—")
        print(f"  {company} — {title}")
        print(f"    Sent: {date_sent}  |  To: {email}")
        print(f"    URL:  {url}")
        print()


def cmd_update(tracker: OutreachTracker, company: str, new_status: str):
    sheets, _ = get_services()
    sheet_id = tracker.sheet_id

    # Read current Jobs tab
    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Jobs!A:Z"
    ).execute()
    rows = result.get("values", [])

    if not rows:
        print("Jobs tab is empty.")
        return

    headers = rows[0]
    company_col = 0   # "Company"
    status_col  = 6   # "Status"

    matches = []
    for i, row in enumerate(rows[1:], start=2):  # row 1 is header, Sheets rows are 1-indexed
        cell = row[company_col].strip().lower() if len(row) > company_col else ""
        if company.lower() in cell:
            matches.append((i, row))

    if not matches:
        print(f"  No application found matching '{company}'.")
        return

    if len(matches) > 1:
        print(f"  Multiple matches for '{company}':")
        for i, row in matches:
            print(f"    Row {i}: {row[0]} — {row[1] if len(row) > 1 else '?'}")
        print("  Be more specific.")
        return

    row_num, row = matches[0]
    old_status = row[status_col].strip() if len(row) > status_col else "—"
    cell_ref = f"Jobs!G{row_num}"   # column G = Status (0-indexed col 6)

    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=cell_ref,
        valueInputOption="USER_ENTERED",
        body={"values": [[new_status]]},
    ).execute()

    print(f"\n  Updated: {row[0]} — {row[1] if len(row) > 1 else '?'}")
    print(f"  Status: {old_status} → {new_status}\n")


def cmd_add(tracker: OutreachTracker, company: str, title: str, url: str,
            location: str = "", email: str = "", notes: str = ""):
    today = date.today().isoformat()
    followup = (date.today() + timedelta(days=4)).isoformat()
    row = [company, title, location, url, email, f"Manual add: {title}", "Sent", today, followup, notes]
    added = tracker.add_rows("Jobs", [row])
    if added:
        print(f"\n  Added: {company} — {title}")
        print(f"  Sheet → {tracker.url()}\n")
    else:
        print(f"\n  Already exists (dedup by URL): {url}\n")


def main():
    parser = argparse.ArgumentParser(prog="job_pipeline")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("report", help="Print funnel summary")

    p_fu = sub.add_parser("followups", help="List overdue follow-ups")
    p_fu.add_argument("--days", type=int, default=4)

    p_up = sub.add_parser("update", help="Update application status")
    p_up.add_argument("--company", required=True)
    p_up.add_argument("--status", required=True, choices=STAGES)

    p_add = sub.add_parser("add", help="Manually add an application")
    p_add.add_argument("--company", required=True)
    p_add.add_argument("--title",   required=True)
    p_add.add_argument("--url",     required=True)
    p_add.add_argument("--location", default="Remote")
    p_add.add_argument("--email",   default="")
    p_add.add_argument("--notes",   default="")

    sub.add_parser("open", help="Print sheet URL")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    tracker = OutreachTracker()

    if args.cmd == "report":
        cmd_report(tracker)
    elif args.cmd == "followups":
        cmd_followups(tracker, days=args.days)
    elif args.cmd == "update":
        cmd_update(tracker, args.company, args.status)
    elif args.cmd == "add":
        cmd_add(tracker, args.company, args.title, args.url,
                location=args.location, email=args.email, notes=args.notes)
    elif args.cmd == "open":
        print(tracker.url())


if __name__ == "__main__":
    main()
