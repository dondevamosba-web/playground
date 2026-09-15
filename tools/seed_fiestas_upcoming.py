#!/usr/bin/env python3
"""
Scrape 3 upcoming BA events from RA and add them as draft rows to the Fiestas tab
in the unified approval sheet.
"""

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
from tools.claude_call import call_claude

SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
TMP = ROOT / ".tmp" / "ra_fiestas_upcoming.json"
AR_TZ = timezone(timedelta(hours=-3))


def get_existing_ids(sheets):
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="'Fiestas'!G2:G100"
    ).execute()
    return {r[0] for r in result.get("values", []) if r}


def scrape_events(limit=15):
    TMP.parent.mkdir(exist_ok=True)
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "scrape_ra_events.py"),
         "--limit", str(limit), "--output", str(TMP)],
        check=True
    )
    return json.loads(TMP.read_text())


def make_caption(event):
    name = event["name"]
    date_str = event["date"]
    venue = event["venue"]
    artists = event.get("artists", [])
    lineup = ", ".join(artists) if artists else ""

    prompt = f"""Write an Instagram caption in Spanish for this upcoming electronic music event in Buenos Aires.

Event: {name}
Date: {date_str}
Venue: {venue}
Lineup: {lineup}

Rules:
- Never start with ¿ or any question mark
- Max 150 words
- Energetic and direct tone
- Include date and venue
- End with 3-5 relevant hashtags like #TechnoBuenosAires #ElectronicMusic #BuenosAires
- No emojis except sparingly at the end
- No placeholder text

Return only the caption text, nothing else."""

    # haiku: caption with explicit rules and constraints, mechanical execution
    return call_claude(prompt, model="haiku")


def main():
    sheets, _ = get_services()
    existing = get_existing_ids(sheets)

    print("Scraping RA events...")
    events = scrape_events()

    rows = []
    for ev in events:
        ra_id = ev.get("event_url", "")
        if ra_id in existing:
            continue

        print(f"  Generating caption for: {ev['name']} ({ev['date']})")
        try:
            caption = make_caption(ev)
        except Exception as e:
            print(f"    Caption error: {e}")
            caption = f"{ev['name']} — {ev['date']} @ {ev['venue']}"

        queued_at = datetime.now(AR_TZ).strftime("%Y-%m-%d %H:%M")
        rows.append([
            queued_at,
            caption,
            ev.get("image_url", ""),
            ev["date"],
            "draft",
            "",
            ra_id,
        ])

        if len(rows) == 3:
            break

    if not rows:
        print("No new events found.")
        return

    sheets.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="'Fiestas'!A2",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows}
    ).execute()

    print(f"\nAdded {len(rows)} upcoming events to Fiestas tab.")


if __name__ == "__main__":
    main()
