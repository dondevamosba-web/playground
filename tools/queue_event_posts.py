#!/usr/bin/env python3
"""
Orchestrator: scrape RA + monitored IG accounts → generate captions → queue to approval sheet.

Run this daily (or on-demand) to discover new events and stage them for review.
Posts land in the Google Sheet with Status="pending". You change to "approved" to publish.

Usage:
  python3 tools/queue_event_posts.py                  # scrape RA + .env IG accounts
  python3 tools/queue_event_posts.py --city buenos-aires
  python3 tools/queue_event_posts.py --skip-ig        # RA only
  python3 tools/queue_event_posts.py --ig-only        # IG accounts only, skip RA
  python3 tools/queue_event_posts.py --dry-run        # show what would be queued

Setup:
  1. Run once, note the sheet URL printed at the end.
  2. Set FIESTAS_APPROVAL_SHEET_ID in .env to avoid recreating the sheet each time.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ID_ENV = "FIESTAS_APPROVAL_SHEET_ID"
AR_TZ = timezone(timedelta(hours=-3))

HEADERS = [
    "Queued At", "Source", "Event Name", "Event Date", "Venue", "City",
    "Lineup", "Feed Caption", "Story Caption", "Image URL", "Source URL",
    "Status", "Post ID", "Notes",
]

COL_EVENT_NAME  = 2   # C (0-based)
COL_EVENT_DATE  = 3   # D
COL_STATUS      = 11  # L
COL_POST_ID     = 12  # M


def get_or_create_sheet(sheets, drive) -> str:
    raw = os.getenv(SHEET_ID_ENV, "").strip()
    # Strip inline comments and validate it looks like a real sheet ID
    sheet_id = raw.split("#")[0].strip()
    if sheet_id and len(sheet_id) > 20 and " " not in sheet_id:
        return sheet_id

    print("Creating new approval sheet...")
    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": "Fiestas — Post Approval Queue"},
        "sheets": [{"properties": {"title": "Queue"}}],
    }).execute()

    sheet_id = spreadsheet["spreadsheetId"]
    print(f"Sheet created. Set in .env:\n  {SHEET_ID_ENV}={sheet_id}")
    print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    # Write headers
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="Queue!A1",
        valueInputOption="RAW",
        body={"values": [HEADERS]},
    ).execute()

    return sheet_id


def existing_event_keys(sheets, sheet_id: str) -> set:
    """Return a set of (event_name, event_date) already in the sheet to prevent duplicates."""
    try:
        resp = sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Queue!C:D",
        ).execute()
        rows = resp.get("values", [])
        return {(r[0].strip(), r[1].strip()) for r in rows[1:] if len(r) >= 2}
    except Exception:
        return set()


def append_rows(sheets, sheet_id: str, rows: list[list]):
    sheets.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Queue!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def run_scraper(script: str, extra_args: list = None) -> list[dict]:
    cmd = [sys.executable, str(ROOT / "tools" / script)] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"  WARN: {script} exited {result.returncode}: {result.stderr.strip()[:300]}")
    if result.stdout:
        for line in result.stdout.splitlines():
            print(f"  [scraper] {line}")
    return []


def load_json_file(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def now_ar() -> str:
    return datetime.now(AR_TZ).strftime("%Y-%m-%d %H:%M")


def events_to_rows(events: list[dict], source: str) -> list[list]:
    rows = []
    for e in events:
        artists = ", ".join(e.get("artists") or [])
        # ghost filter: no venue, no lineup AND no source URL means
        # unverifiable scraper noise ("SIN VENTA", "Sugar Crush Remix") — skip
        if not (e.get("venue") or "").strip() and not artists \
                and not (e.get("event_url") or e.get("post_url") or "").strip():
            print(f"  [ghost] salteado: {e.get('name', '?')[:50]}")
            continue
        rows.append([
            now_ar(),                          # A Queued At
            source,                            # B Source
            e.get("name", ""),                 # C Event Name
            e.get("date", ""),                 # D Event Date
            e.get("venue", ""),                # E Venue
            e.get("city", "Buenos Aires"),     # F City
            artists,                           # G Lineup
            e.get("feed_caption", ""),         # H Feed Caption
            e.get("story_caption", ""),        # I Story Caption
            e.get("image_url", ""),            # J Image URL
            e.get("event_url", e.get("post_url", "")),  # K Source URL
            "pending",                         # L Status
            "",                                # M Post ID
            "",                                # N Notes
        ])
    return rows


def main():
    parser = argparse.ArgumentParser(description="Queue event posts to approval sheet")
    parser.add_argument("--city", default=None, help="RA city filter e.g. buenos-aires")
    parser.add_argument("--skip-ig", action="store_true", help="Skip IG account scraping")
    parser.add_argument("--ig-only", action="store_true", help="Skip RA, scrape IG accounts only")
    parser.add_argument("--skip-tm", action="store_true", help="Skip Ticketmaster AR scraping")
    parser.add_argument("--skip-passline", action="store_true", help="Skip Passline scraping")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be queued, don't write")
    args = parser.parse_args()

    sheets_svc, drive_svc = get_services()
    sheet_id = get_or_create_sheet(sheets_svc, drive_svc)

    known = existing_event_keys(sheets_svc, sheet_id)
    print(f"Sheet has {len(known)} existing entries.")

    all_events = []

    # --- RA scrape ---
    if not args.ig_only:
        print("\nScraping Resident Advisor Argentina...")
        extra = ["--output", ".tmp/ra_events.json"]
        if args.city:
            extra += ["--city", args.city]
        run_scraper("scrape_ra_events.py", extra)

        ra_events = load_json_file(".tmp/ra_events.json")
        print(f"  {len(ra_events)} RA events scraped")

        # Generate captions
        if ra_events:
            print("  Generating captions...")
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "generate_event_caption.py"),
                 "--input", ".tmp/ra_events.json",
                 "--output", ".tmp/ra_events_captioned.json"],
                cwd=str(ROOT), capture_output=False,
            )
            ra_events = load_json_file(".tmp/ra_events_captioned.json") or ra_events

        for e in ra_events:
            key = (e.get("name", "").strip(), e.get("date", "").strip())
            if key not in known and key[0]:
                all_events.append(("Resident Advisor", e))

    # --- Ticketmaster AR scrape ---
    if not args.ig_only and not args.skip_tm:
        tm_api_key = os.getenv("TM_API_KEY", "").strip()
        if tm_api_key:
            print("\nScraping Ticketmaster (Argentina, electronic)...")
            run_scraper("scrape_ticketmaster_ar.py", ["--output", ".tmp/tm_ar_events.json"])

            tm_events = load_json_file(".tmp/tm_ar_events.json")
            print(f"  {len(tm_events)} Ticketmaster events scraped")

            for e in tm_events:
                key = (e.get("name", "").strip(), e.get("date", "").strip())
                if key not in known and key[0]:
                    all_events.append(("Ticketmaster AR", e))
                    known.add(key)
        else:
            print("\nTicketmaster skipped — set TM_API_KEY in .env to enable.")
            print("  Get a free key at: https://developer.ticketmaster.com/")

    # --- Passline scrape ---
    if not args.ig_only and not args.skip_passline:
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "").strip()
        if firecrawl_key:
            print("\nScraping Passline (electronic)...")
            run_scraper("scrape_passline.py", ["--output", ".tmp/passline_events.json"])

            passline_events = load_json_file(".tmp/passline_events.json")
            print(f"  {len(passline_events)} Passline events scraped")

            for e in passline_events:
                key = (e.get("name", "").strip(), e.get("date", "").strip())
                if key not in known and key[0]:
                    all_events.append(("Passline", e))
                    known.add(key)
        else:
            print("\nPassline skipped — FIRECRAWL_API_KEY not set in .env.")

    # --- IG accounts scrape ---
    if not args.skip_ig:
        source_accounts = os.getenv("FIESTAS_IG_SOURCE_ACCOUNTS", "").strip()
        if source_accounts:
            print(f"\nScraping IG accounts: {source_accounts}")
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "scrape_ig_posts.py"),
                 "--output", ".tmp/ig_posts.json"],
                cwd=str(ROOT), capture_output=False,
            )

            ig_posts = load_json_file(".tmp/ig_posts.json")
            event_posts = [p for p in ig_posts if p.get("is_event")]
            print(f"  {len(event_posts)} event posts from IG accounts")

            # Generate captions for IG reposts
            if event_posts:
                # Convert IG posts to event-like dicts for caption generator
                for post in event_posts:
                    post.setdefault("name", post.get("caption", "")[:60] + "...")
                    post.setdefault("venue", "")
                    post.setdefault("city", "Buenos Aires")

                with open(".tmp/ig_events.json", "w", encoding="utf-8") as f:
                    json.dump(event_posts, f, ensure_ascii=False)

                subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "generate_event_caption.py"),
                     "--input", ".tmp/ig_events.json",
                     "--output", ".tmp/ig_events_captioned.json"],
                    cwd=str(ROOT), capture_output=False,
                )
                event_posts = load_json_file(".tmp/ig_events_captioned.json") or event_posts

            source_label = f"IG @{event_posts[0].get('source_account', '?')}" if event_posts else "IG"
            for e in event_posts:
                key = (e.get("name", "").strip(), e.get("event_date", "").strip())
                if key[0]:
                    all_events.append((f"IG @{e.get('source_account', '?')}", e))
        else:
            print("\nNo IG source accounts configured. Set FIESTAS_IG_SOURCE_ACCOUNTS in .env to enable.")

    if not all_events:
        print("\nNo new events to queue.")
        return

    print(f"\n{len(all_events)} new events to queue:")
    rows = []
    for source, event in all_events:
        print(f"  [{source}] {event.get('name')} — {event.get('date', event.get('event_date', '?'))}")
        event_rows = events_to_rows([event], source)
        rows.extend(event_rows)

    if args.dry_run:
        print("\n[DRY RUN] Would write the above rows to the sheet.")
        return

    append_rows(sheets_svc, sheet_id, rows)
    print(f"\nQueued {len(rows)} posts → review at:")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    print("\nChange Status column from 'pending' to 'approved' to publish.")


if __name__ == "__main__":
    main()
