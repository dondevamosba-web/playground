#!/usr/bin/env python3
"""
Create or update the Storm Digital content calendar in Google Sheets.
Generates posts targeting US home service contractors (roofing, HVAC, windows, plumbing).

Usage:
  python3 tools/fill_content_storm.py                  # 4 weeks from today
  python3 tools/fill_content_storm.py --weeks 8
  python3 tools/fill_content_storm.py --dry-run        # print without writing
  python3 tools/fill_content_storm.py --sheet-id XXXX  # use specific sheet
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.claude_call import call_claude

SHEET_TITLE   = "Storm Digital — Content Calendar"
SHEET_ENV_KEY = "STORM_CONTENT_CALENDAR_SHEET_ID"

# (weekday 0=Mon, time_str ET UTC-5, post_type, content_type)
WEEKLY_SLOTS = [
    (0, "09:00", "reel",     "Educational tip: digital marketing for home service contractors"),
    (2, "12:00", "carousel", "List post: mistakes, checklist, or step-by-step for contractors"),
    (3, "17:00", "reel",     "Result or stat: client win, industry benchmark, ROI proof"),
    (4, "11:00", "single",   "Authority post: industry insight or market trend"),
    (5, "10:00", "carousel", "Service spotlight: roofing, HVAC, windows, or plumbing focus"),
]

HASHTAGS = (
    "#StormDigital #HomeServices #ContractorMarketing #RoofingMarketing "
    "#HVACMarketing #GoogleAds #LocalSEO #LeadGeneration #ContractorLife "
    "#SmallBusiness #DigitalMarketing #HomeImprovement #Roofing #HVAC"
)

BRAND_CONTEXT = """
Storm Digital (storm.mkt.agency) is a US digital marketing agency that exclusively serves home service contractors — roofing, HVAC, windows, plumbing, and related trades.

Target audience: owners of home service companies, 5–50 employees, spending $2k–$20k/mo on marketing.
Tone: direct, confident, results-oriented. No jargon. No fluff. Speak like a contractor who also knows marketing.
Language: English (US).
Goal: generate inbound leads and establish authority in contractor marketing.

Services: Google Ads, Local SEO, Google Business Profile optimization, conversion-focused websites, review generation, call tracking.

Proof points to weave in when relevant:
- Average CPL for roofing: $38 (vs. industry $120+)
- 3× lead volume for HVAC client in 60 days
- 270% more clicks with 50+ Google reviews
- Average client ROI: 8×
"""

VERTICALS = ["roofing", "HVAC", "windows", "plumbing", "general contractors"]


def generate_caption(content_type: str, post_number: int) -> str:
    # Rotate verticals so different ones appear through the calendar
    vertical = VERTICALS[(post_number - 1) % len(VERTICALS)]

    prompt = f"""Write an Instagram caption for Storm Digital.

{BRAND_CONTEXT}

Post type: {content_type}
Primary vertical this post: {vertical}
Post number in sequence: {post_number}

Rules:
- Maximum 120 words
- First line: strong hook (no emojis, no question mark clichés)
- 2–3 lines of concrete value or proof
- CTA at the end: DM "AUDIT" for a free review, or visit storm.mkt.agency
- No hashtags (added separately)
- Direct tone, no empty phrases like "in today's digital landscape"
- Write in English

Return only the caption text, no quotes, no explanation."""

    return call_claude(prompt, model="haiku")


def build_rows(start: date, weeks: int, dry_run: bool) -> list[list]:
    rows = []
    post_number = 1
    for week in range(weeks):
        for weekday, time_str, post_type, content_type in WEEKLY_SLOTS:
            days_offset = (week * 7) + (weekday - start.weekday()) % 7
            post_date = start + timedelta(days=days_offset)

            if dry_run:
                caption = f"[DRY RUN] {content_type[:60]}"
            else:
                print(f"  Generating post {post_number}: {content_type[:50]}...")
                caption = generate_caption(content_type, post_number)

            day_name = post_date.strftime("%A")
            rows.append([
                post_date.strftime("%Y-%m-%d"),
                time_str,
                day_name,
                content_type,
                post_type,
                caption,
                HASHTAGS,
                "",  # Media URL (filled when media is ready)
                "pending",
                "",  # Post ID (filled after publishing)
            ])
            post_number += 1
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", type=int, default=8,
                        help="Number of weeks to fill (default: 8 = 40 posts)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sheet-id", default=None)
    args = parser.parse_args()

    sheet_id = args.sheet_id or os.getenv(SHEET_ENV_KEY)
    if not sheet_id:
        print(f"ERROR: {SHEET_ENV_KEY} not set in .env and --sheet-id not provided.")
        sys.exit(1)

    start = date.today()
    # Start on Monday of the current or next week
    days_to_monday = (7 - start.weekday()) % 7
    if days_to_monday == 0:
        days_to_monday = 7
    start = start + timedelta(days=days_to_monday)

    total = args.weeks * len(WEEKLY_SLOTS)
    print(f"Generating {total} posts over {args.weeks} weeks starting {start}...")
    if args.dry_run:
        print("(DRY RUN — captions will not be generated)")

    rows = build_rows(start, args.weeks, args.dry_run)

    if args.dry_run:
        for row in rows:
            print(f"  {row[0]} {row[1]} [{row[4]}] {row[3][:50]}")
        print(f"\n{len(rows)} rows would be written to sheet {sheet_id}")
        return

    sheets, _ = get_services()

    # Write header row + data
    header = [["Date", "Time", "Day", "Content Type", "Post Type",
               "Caption", "Hashtags", "Media URL", "Status", "Post ID"]]
    all_rows = header + rows

    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body={"values": all_rows},
    ).execute()

    print(f"\nDone. {len(rows)} posts written to sheet:")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    main()
