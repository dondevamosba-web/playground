#!/usr/bin/env python3
"""
Follow-up scheduler: finds overdue leads across all niche tabs and generates bump drafts.

Reads from "Outreach Tracker" (Jobs / Roofing / HVAC tabs).
Flags rows where Status = "Sent" and 5+ days have passed with no reply.
Generates a short bump email via Claude and saves it as a Gmail draft.

Usage:
  python3 tools/check_followups.py              # check + generate bump drafts
  python3 tools/check_followups.py --dry-run    # check only, no drafts created
  python3 tools/check_followups.py --all        # show full pipeline summary
  python3 tools/check_followups.py --days 7     # override the 5-day default
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.outreach_tracker import OutreachTracker, TABS
from tools.claude_call import call_claude
from tools.gmail_draft import create_draft, build_html_body

DEFAULT_DAYS = 5


def _get_days():
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        try:
            return int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            pass
    return DEFAULT_DAYS


def generate_bump(niche: str, lead: dict) -> tuple:
    """Return (to, subject, plain_body) for a bump email."""
    if niche == "Jobs":
        company = lead.get("Company", "")
        job_title = lead.get("Job Title", "")
        email_to = lead.get("Email To", "")
        orig_subject = lead.get("Subject", f"Application for {job_title}")
        prompt = (
            f"Write a short follow-up email (2-3 sentences max) to {company} about a {job_title} position. "
            "The sender is Guido Carminatti, a senior performance marketing specialist with 8 years of experience. "
            "Tone: warm, professional, not desperate. One clear ask: confirm receipt and express continued interest. "
            "Return ONLY the email body — no subject line, no salutation header."
        )
        return email_to, f"Re: {orig_subject}", call_claude(prompt, model="haiku")

    else:
        company = lead.get("Company", "")
        city = lead.get("City", "")
        email = lead.get("Email", "")
        prompt = (
            f"Write a short follow-up email (2-3 sentences max) to the owner of {company}, "
            f"a {niche.lower()} company in {city}. "
            "This follows a cold outreach from Guido at Storm Digital, a paid ads agency that generates "
            "exclusive leads for home service companies. "
            "Tone: casual, low pressure, no pitching. Just a friendly check-in with one simple re-engagement question. "
            "Return ONLY the email body — no subject line, no salutation header."
        )
        subject = f"Re: Exclusive {niche} Leads in {city}"
        return email, subject, call_claude(prompt, model="haiku")


def main():
    dry_run = "--dry-run" in sys.argv
    show_all = "--all" in sys.argv
    days = _get_days()

    tracker = OutreachTracker()

    if show_all:
        summary = tracker.pipeline_summary()
        print("Pipeline summary")
        print("=" * 40)
        for tab, counts in summary.items():
            if not counts:
                print(f"\n{tab}: (empty)")
                continue
            print(f"\n{tab}:")
            for status, n in sorted(counts.items()):
                print(f"  {status:<22} {n}")
        print(f"\nSheet: {tracker.url()}")
        return

    total_overdue = 0
    drafts_created = 0

    for niche in TABS:
        overdue = tracker.get_overdue(niche, days=days)
        if not overdue:
            continue

        total_overdue += len(overdue)
        print(f"\n{niche} — {len(overdue)} overdue (>{days}d no reply)")
        print("-" * 50)

        for lead in overdue:
            company = lead.get("Company") or lead.get("Job Title", "")
            email = lead.get("Email To") or lead.get("Email", "")
            date_sent = lead.get("Date Sent") or lead.get("Date Added", "")
            print(f"  {company} | {email} | sent {date_sent}")

            if not dry_run and email:
                try:
                    to, subject, body = generate_bump(niche, lead)
                    html = build_html_body(body)
                    result = create_draft(to=to, subject=subject, body=html, html=True)
                    print(f"    → Draft created ({result['draft_id']})")
                    drafts_created += 1
                except Exception as e:
                    print(f"    → Failed to create draft: {e}")

    if total_overdue == 0:
        print(f"No follow-ups overdue (threshold: {days} days).")
    else:
        label = "would create" if dry_run else "created"
        print(f"\n{total_overdue} overdue lead(s) found. {drafts_created} bump draft(s) {label}.")

    print(f"\nSheet: {tracker.url()}")


if __name__ == "__main__":
    main()
