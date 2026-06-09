#!/usr/bin/env python3
"""
Syncs .tmp/email_drafts.json into the "Jobs" tab of the unified Outreach Tracker sheet.

Adds new drafts as rows; never overwrites existing rows (preserves manual edits).
Deduplicates by Job URL.

Status lifecycle: Drafted → Sent → Replied → Interview Scheduled → Offer | Rejected | Ghosted

Usage:
  python3 tools/log_outreach.py           # sync drafts, print sheet URL
  python3 tools/log_outreach.py --url     # print sheet URL only (no sync)
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.outreach_tracker import OutreachTracker

DRAFTS_JSON = ROOT / ".tmp" / "email_drafts.json"


def main():
    url_only = "--url" in sys.argv
    tracker = OutreachTracker()

    if url_only:
        print(tracker.url())
        return

    if not DRAFTS_JSON.exists():
        print(f"No drafts found at {DRAFTS_JSON}. Run generate_email_drafts.py first.")
        sys.exit(1)

    with open(DRAFTS_JSON) as f:
        drafts = json.load(f)

    today = date.today().isoformat()
    rows = [
        [
            d.get("company", ""),
            d.get("job_title", ""),
            d.get("location", ""),
            d.get("job_url", ""),
            d.get("to", ""),
            d.get("subject", ""),
            "Drafted",
            today,
            "",  # Follow-up Date
            "",  # Notes
        ]
        for d in drafts
        if d.get("job_url")
    ]

    added = tracker.add_rows("Jobs", rows)
    if added:
        print(f"Added {added} new row(s) to Outreach Tracker → Jobs.")
    else:
        print("Sheet is already up to date — no new drafts to add.")

    print(f"\nSheet URL: {tracker.url()}")


if __name__ == "__main__":
    main()
