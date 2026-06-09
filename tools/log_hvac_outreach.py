"""
Syncs HVAC leads into the "HVAC" tab of the unified Outreach Tracker sheet.

Adds drafted leads as rows; never overwrites existing rows (preserves manual edits).
Deduplicates by email.

Status lifecycle: Drafted → Sent → Replied → Call Booked → Closed | Lost | Ghosted

Usage:
  python3 tools/log_hvac_outreach.py           # sync drafted leads, print sheet URL
  python3 tools/log_hvac_outreach.py --url     # print sheet URL only
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.outreach_tracker import OutreachTracker

LEADS_JSON = ROOT / ".tmp" / "hvac_leads.json"


def main():
    url_only = "--url" in sys.argv
    tracker = OutreachTracker()

    if url_only:
        print(tracker.url())
        return

    if not LEADS_JSON.exists():
        print(f"No leads found at {LEADS_JSON}. Run scrape_hvac_gmaps.py first.")
        sys.exit(1)

    leads = json.loads(LEADS_JSON.read_text())
    leads_with_email = [l for l in leads if l.get("email")]

    today = date.today().isoformat()
    rows = [
        [
            l.get("name", ""),
            l.get("city", ""),
            l.get("email", ""),
            l.get("phone", "") or "",
            l.get("website", "") or "",
            l.get("rating", "") or "",
            l.get("fb_ads_status", "") or "",
            "Drafted",
            today,
            "",  # Follow-up Date
            "",  # Notes
        ]
        for l in leads_with_email
    ]

    added = tracker.add_rows("HVAC", rows)
    if added:
        print(f"Added {added} new leads to Outreach Tracker → HVAC.")
    else:
        print("No new leads to add.")

    print(f"\nSheet URL: {tracker.url()}")


if __name__ == "__main__":
    main()
