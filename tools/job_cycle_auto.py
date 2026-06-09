"""
Full job search automation in one command.

Steps:
  1. Scrape LATAM-friendly remote job boards (scrape_latam_remote_jobs.run)
  2. Run job_cycle.py as subprocess (avoids module-level side effects)
  3. Read cycle_log.json for new drafts
  4. Read latam_remote_jobs.json for LATAM lead counts
  5. Read OutreachTracker for pipeline funnel + follow-ups due
  6. Find and email active recruiters via Apollo (find_recruiters.py)
  7. Create a Gmail digest draft to dondevamosba@gmail.com

Usage:
    python3 tools/job_cycle_auto.py
    python3 tools/job_cycle_auto.py --pages 4
    python3 tools/job_cycle_auto.py --dry-run
    python3 tools/job_cycle_auto.py --no-scrape        # use existing latam data
    python3 tools/job_cycle_auto.py --no-recruiters    # skip recruiter outreach
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

DIGEST_TO = "dondevamosba@gmail.com"

STAGES = ["Drafted", "Sent", "Replied", "Interview Scheduled", "Offer", "Rejected", "Ghosted"]


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def step_scrape_latam():
    """Import and run scrape_latam_remote_jobs.run(). Returns (open_count, unknown_count)."""
    from scrape_latam_remote_jobs import run as scrape_run
    scrape_run()

    output_json = TMP / "latam_remote_jobs.json"
    if not output_json.exists():
        return 0, 0
    with open(output_json, encoding="utf-8") as f:
        jobs = json.load(f)
    open_count    = sum(1 for j in jobs if j.get("relevant") and j.get("latam_status") == "open")
    unknown_count = sum(1 for j in jobs if j.get("relevant") and j.get("latam_status") == "unknown")
    return open_count, unknown_count


def read_latam_counts():
    """Read existing latam_remote_jobs.json without re-scraping."""
    output_json = TMP / "latam_remote_jobs.json"
    if not output_json.exists():
        return 0, 0
    with open(output_json, encoding="utf-8") as f:
        jobs = json.load(f)
    open_count    = sum(1 for j in jobs if j.get("relevant") and j.get("latam_status") == "open")
    unknown_count = sum(1 for j in jobs if j.get("relevant") and j.get("latam_status") == "unknown")
    return open_count, unknown_count


def step_job_cycle(pages: int, dry_run: bool):
    """Run job_cycle.py as a subprocess. Returns returncode."""
    cmd = [sys.executable, str(ROOT / "tools" / "job_cycle.py"), "--pages", str(pages)]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode


def read_cycle_log():
    """Return list of drafts from cycle_log.json, or empty list."""
    log_path = TMP / "cycle_log.json"
    if not log_path.exists():
        return []
    with open(log_path, encoding="utf-8") as f:
        return json.load(f)


def get_pipeline_data():
    """Return (funnel_dict, overdue_list) from OutreachTracker."""
    from outreach_tracker import OutreachTracker
    tracker = OutreachTracker()
    summary = tracker.pipeline_summary()
    funnel = summary.get("Jobs", {})
    overdue = tracker.get_overdue("Jobs", days=4)
    return funnel, overdue


# ---------------------------------------------------------------------------
# Digest builder
# ---------------------------------------------------------------------------

def build_digest(latam_open, latam_unknown, cycle_drafts, funnel, overdue, dry_run, recruiter_drafts=None):
    today = date.today().isoformat()

    new_draft_count = len(cycle_drafts)
    pushed_count    = sum(1 for d in cycle_drafts if d.get("draft_id"))

    lines = [
        f"<h2>Job Search Digest — {today}</h2>",
        "<hr>",

        "<h3>LATAM Remote Leads (from job boards)</h3>",
        "<ul>",
        f"  <li>LATAM/Worldwide confirmed: <strong>{latam_open}</strong></li>",
        f"  <li>Location unclear (worth contacting): <strong>{latam_unknown}</strong></li>",
        f"  <li>Total actionable: <strong>{latam_open + latam_unknown}</strong></li>",
        "</ul>",

        "<h3>Job Cycle — New Drafts</h3>",
        "<ul>",
        f"  <li>Emails generated: <strong>{new_draft_count}</strong></li>",
    ]
    if not dry_run:
        lines.append(f"  <li>Gmail drafts created: <strong>{pushed_count}</strong></li>")
    lines.append("</ul>")

    # Funnel snapshot
    lines += ["<h3>Pipeline Funnel</h3>", "<ul>"]
    total = sum(funnel.values())
    for stage in STAGES:
        count = funnel.get(stage, 0)
        if count:
            lines.append(f"  <li>{stage}: <strong>{count}</strong></li>")
    for stage, count in funnel.items():
        if stage not in STAGES and stage and count:
            lines.append(f"  <li>{stage}: <strong>{count}</strong></li>")
    lines.append(f"  <li><em>Total tracked: {total}</em></li>")
    lines.append("</ul>")

    # New drafts list
    if cycle_drafts:
        lines += ["<h3>New Drafts Created This Run</h3>", "<ol>"]
        for d in cycle_drafts:
            company = d.get("company", "—")
            title   = d.get("title", "—")
            url     = d.get("url", "")
            link    = f'<a href="{url}">{company}</a>' if url else company
            lines.append(f"  <li>{link} — {title}</li>")
        lines.append("</ol>")
    else:
        lines.append("<p><em>No new drafts this run.</em></p>")

    # Follow-ups due
    lines.append("<h3>Follow-ups Due (4+ days, no update)</h3>")
    if overdue:
        lines.append("<ul>")
        for r in overdue:
            company   = r.get("Company", "—")
            title     = r.get("Job Title", "—")
            date_sent = r.get("Date Added", "—")
            lines.append(f"  <li><strong>{company}</strong> — {title} (sent {date_sent})</li>")
        lines.append("</ul>")
    else:
        lines.append("<p><em>None — you're up to date.</em></p>")

    # Recruiter outreach section
    recruiter_drafts = recruiter_drafts or []
    lines.append("<h3>Recruiter Outreach (Apollo)</h3>")
    if recruiter_drafts:
        lines += [f"<p>{len(recruiter_drafts)} new recruiter draft(s) created in Gmail.</p>", "<ul>"]
        for r in recruiter_drafts:
            name = r.get("name", "—")
            title = r.get("title", "")
            company = r.get("company", "")
            lines.append(f"  <li><strong>{name}</strong> — {title} @ {company}</li>")
        lines.append("</ul>")
    else:
        lines.append("<p><em>No new recruiters this run (all already contacted or Apollo returned none).</em></p>")

    if dry_run:
        lines.append("<p><em>[DRY RUN — no Gmail drafts were created]</em></p>")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Full job search automation + daily digest")
    parser.add_argument("--pages",          type=int, default=2, help="Pages per LinkedIn query (default: 2)")
    parser.add_argument("--dry-run",        action="store_true", help="Skip Gmail draft creation")
    parser.add_argument("--no-scrape",      action="store_true", help="Skip LATAM scrape, use existing data")
    parser.add_argument("--no-recruiters",  action="store_true", help="Skip recruiter outreach step")
    parser.add_argument("--recruiter-limit", type=int, default=15, help="Max new recruiters to email per run (default: 15)")
    args = parser.parse_args()

    today = date.today().isoformat()
    print("=" * 60)
    print(f"JOB CYCLE AUTO — {today}")
    print("=" * 60)

    # Step 1: LATAM scrape
    if args.no_scrape:
        print("\n[1/5] Skipping LATAM scrape — using existing data...")
        latam_open, latam_unknown = read_latam_counts()
    else:
        print("\n[1/5] Scraping LATAM remote job boards...")
        latam_open, latam_unknown = step_scrape_latam()
    print(f"  LATAM open: {latam_open}  |  Unknown: {latam_unknown}")

    # Step 2: job_cycle
    print(f"\n[2/5] Running job_cycle.py --pages {args.pages}...")
    rc = step_job_cycle(pages=args.pages, dry_run=args.dry_run)
    if rc != 0:
        print(f"  WARNING: job_cycle.py exited with code {rc}")

    # Step 3: Read cycle log
    print("\n[3/5] Reading cycle log...")
    cycle_drafts = read_cycle_log()
    print(f"  Drafts in log: {len(cycle_drafts)}")

    # Step 4: Recruiter outreach via Apollo
    recruiter_drafts = []
    if args.no_recruiters:
        print("\n[4/6] Skipping recruiter outreach (--no-recruiters).")
    else:
        print(f"\n[4/6] Finding & emailing recruiters via Apollo (limit: {args.recruiter_limit})...")
        try:
            from find_recruiters import run as find_recruiters_run
            recruiter_drafts = find_recruiters_run(dry_run=args.dry_run, limit=args.recruiter_limit)
            print(f"  Recruiter drafts: {len(recruiter_drafts)}")
        except Exception as e:
            print(f"  WARNING: Recruiter step failed — {e}")

    # Step 5+6: Pipeline data
    print("\n[5/6] Reading pipeline data...")
    try:
        funnel, overdue = get_pipeline_data()
        print(f"  Funnel stages: {len(funnel)}  |  Follow-ups due: {len(overdue)}")
    except Exception as e:
        print(f"  WARNING: Could not read pipeline — {e}")
        funnel, overdue = {}, []

    # Step 6: Gmail digest
    subject = f"Job Search Digest — {today}"
    html_body = build_digest(latam_open, latam_unknown, cycle_drafts, funnel, overdue, args.dry_run, recruiter_drafts)

    if args.dry_run:
        print(f"\n[6/6] Dry run — skipping Gmail digest.")
        print(f"\n  Subject: {subject}")
        print("  (Use without --dry-run to send digest to Gmail)")
    else:
        print(f"\n[6/6] Creating Gmail digest draft...")
        from gmail_draft import create_draft
        try:
            result = create_draft(to=DIGEST_TO, subject=subject, body=html_body, html=True)
            print(f"  Draft created: {result.get('draft_id', '?')}")
        except Exception as e:
            print(f"  ERROR creating digest draft: {e}")

    print(f"\n{'=' * 60}")
    print("AUTO CYCLE COMPLETE")
    print(f"  LATAM leads (open + unknown): {latam_open + latam_unknown}")
    print(f"  New job drafts:               {len(cycle_drafts)}")
    print(f"  Recruiter drafts:             {len(recruiter_drafts)}")
    print(f"  Follow-ups due:               {len(overdue)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
