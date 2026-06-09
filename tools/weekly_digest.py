#!/usr/bin/env python3
"""
Weekly personal dashboard — one Gmail draft every Monday with a summary of:
  - Job pipeline: new drafts, applications sent, follow-ups due
  - Storm Digital: inbound leads by tier, outbound pipeline by niche
  - Fiestas: events queued and published this week

Usage:
  python3 tools/weekly_digest.py          # full run
  python3 tools/weekly_digest.py --dry-run  # print digest, skip Gmail
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.claude_call import call_claude
from tools.gmail_draft import create_draft
from tools.outreach_tracker import OutreachTracker

TMP = ROOT / ".tmp"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _read_json(path):
    p = Path(path)
    if p.exists() and p.stat().st_size > 2:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def _week_range():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    return week_start.isoformat(), today.isoformat()


# ── Data collectors ────────────────────────────────────────────────────────────

def jobs_section(tracker: OutreachTracker) -> dict:
    week_start, today = _week_range()

    # Latest cycle run
    cycle = _read_json(TMP / "cycle_log.json") or []
    new_this_run = len(cycle)
    drafts_created = sum(1 for j in cycle if j.get("draft_id"))

    # Seen jobs total
    seen = _read_json(TMP / "seen_jobs.json") or {}
    total_seen = len(seen.get("urls", []))

    # Pipeline status from sheet
    pipeline = tracker.pipeline_summary().get("Jobs", {})

    # Follow-ups due
    overdue = tracker.get_overdue("Jobs", days=4)

    return {
        "new_this_run": new_this_run,
        "drafts_created": drafts_created,
        "total_seen": total_seen,
        "pipeline": pipeline,
        "followups_due": len(overdue),
        "followup_companies": [r.get("Company", "") for r in overdue[:5]],
    }


def storm_section(tracker: OutreachTracker) -> dict:
    # Outbound pipeline
    pipeline = tracker.pipeline_summary()
    storm = {niche: pipeline.get(niche, {}) for niche in ["Roofing", "HVAC", "Plumbing"]}

    # Inbound leads
    inbound = _read_json(TMP / "inbound_leads.json") or []
    tier_counts = {"A": 0, "B": 0, "C": 0, "unscored": 0}
    new_this_week = 0
    week_start = (_week_range()[0])
    for lead in inbound:
        tier = lead.get("tier", "")
        if tier in tier_counts:
            tier_counts[tier] += 1
        else:
            tier_counts["unscored"] += 1
        added = lead.get("date_added", lead.get("submitted_at", ""))
        if added and str(added)[:10] >= week_start:
            new_this_week += 1

    return {
        "outbound": storm,
        "inbound_tiers": tier_counts,
        "inbound_new_this_week": new_this_week,
        "inbound_total": len(inbound),
    }


def fiestas_section() -> dict:
    events = (
        _read_json(TMP / "ra_events_captioned.json")
        or _read_json(TMP / "ra_events.json")
        or []
    )
    week_start = _week_range()[0]
    queued = sum(1 for e in events if e.get("status", "pending") == "pending")
    approved = sum(1 for e in events if e.get("status") == "approved")
    published_this_week = sum(
        1 for e in events
        if e.get("status") == "published"
        and str(e.get("published_at", ""))[:10] >= week_start
    )
    return {
        "total_events": len(events),
        "queued": queued,
        "approved": approved,
        "published_this_week": published_this_week,
    }


# ── Claude summary ─────────────────────────────────────────────────────────────

def build_summary(jobs: dict, storm: dict, fiestas: dict) -> str:
    job_pipeline_str = ", ".join(
        f"{status}: {count}" for status, count in jobs["pipeline"].items()
    ) or "no data"

    storm_outbound_str = "\n".join(
        f"  {niche}: " + ", ".join(f"{s}: {c}" for s, c in counts.items())
        for niche, counts in storm["outbound"].items()
    ) or "  no data"

    prompt = f"""You're writing a brief weekly dashboard for Guido — a paid media specialist and agency owner.
Summarize the week in 3 short bullets (1 sentence each). Be direct, no fluff.

JOB SEARCH
- New jobs found this run: {jobs['new_this_run']}
- Drafts created: {jobs['drafts_created']}
- Total jobs seen (lifetime): {jobs['total_seen']}
- Pipeline: {job_pipeline_str}
- Follow-ups overdue: {jobs['followups_due']} ({', '.join(jobs['followup_companies']) or 'none'})

STORM DIGITAL OUTBOUND
{storm_outbound_str}

STORM DIGITAL INBOUND
- New leads this week: {storm['inbound_new_this_week']}
- Tier A: {storm['inbound_tiers']['A']}, Tier B: {storm['inbound_tiers']['B']}, Tier C: {storm['inbound_tiers']['C']}

FIESTAS
- Events queued for approval: {fiestas['queued']}
- Events approved: {fiestas['approved']}
- Posts published this week: {fiestas['published_this_week']}

Write 3 bullets:
• Job search: one insight or action item
• Storm: one insight or action item
• Fiestas: one line on status
"""
    return call_claude(prompt, model="haiku")


# ── Email builder ──────────────────────────────────────────────────────────────

def build_body(jobs: dict, storm: dict, fiestas: dict, summary: str, today: str) -> str:
    def _pipeline_rows(data: dict) -> str:
        if not data:
            return "  (no data)"
        return "\n".join(f"  {status:<18} {count}" for status, count in data.items())

    followups = (
        "\n".join(f"  • {c}" for c in jobs["followup_companies"])
        if jobs["followup_companies"] else "  none"
    )

    storm_outbound = "\n".join(
        f"\n  [{niche}]\n" + "\n".join(f"    {s:<16} {c}" for s, c in counts.items())
        for niche, counts in storm["outbound"].items()
    )

    return f"""WEEKLY DIGEST — {today}
{"=" * 50}

SUMMARY
{summary}

{"=" * 50}
JOB PIPELINE
{"─" * 40}
New jobs this run:    {jobs['new_this_run']}
Drafts created:       {jobs['drafts_created']}
Total seen (lifetime): {jobs['total_seen']}

Pipeline breakdown:
{_pipeline_rows(jobs['pipeline'])}

Follow-ups overdue ({jobs['followups_due']}):
{followups}

{"=" * 50}
STORM DIGITAL
{"─" * 40}
INBOUND
  New this week:   {storm['inbound_new_this_week']}
  Tier A:          {storm['inbound_tiers']['A']}
  Tier B:          {storm['inbound_tiers']['B']}
  Tier C:          {storm['inbound_tiers']['C']}
  Total:           {storm['inbound_total']}

OUTBOUND{storm_outbound}

{"=" * 50}
FIESTAS
{"─" * 40}
Events queued:     {fiestas['queued']}
Events approved:   {fiestas['approved']}
Published (week):  {fiestas['published_this_week']}
"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today = date.today().isoformat()
    print(f"Weekly Digest — {today}")
    print("Pulling data...")

    tracker = OutreachTracker()
    jobs = jobs_section(tracker)
    storm = storm_section(tracker)
    fiestas = fiestas_section()

    print("Generating summary...")
    summary = build_summary(jobs, storm, fiestas)
    body = build_body(jobs, storm, fiestas, summary, today)

    print("\n" + body)

    if args.dry_run:
        print("\n[dry-run] Skipping Gmail draft.")
        return

    subject = f"Weekly Digest — {today}"
    result = create_draft(to="dondevamosba@gmail.com", subject=subject, body=body)
    print(f"\nDraft created: {result['draft_id']}")
    print("Done.")


if __name__ == "__main__":
    main()
