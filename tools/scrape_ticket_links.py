#!/usr/bin/env python3
"""
Extract ticket URLs from Fiestas captions and venue post links.

Looks for Ticketmaster, Eventbrite, and direct venue ticket links.
Adds "Entradas: [URL]" to feed captions if not already present.

Usage:
  python3 tools/scrape_ticket_links.py              # Scan & report
  python3 tools/scrape_ticket_links.py --apply      # Apply to pending posts
"""
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

# Patterns for ticket URLs
TICKET_PATTERNS = [
    r"https?://[a-z0-9.-]*ticketmaster[a-z0-9.-]*/[^\s]+",
    r"https?://[a-z0-9.-]*eventbrite[a-z0-9.-]*/[^\s]+",
    r"https?://[a-z0-9.-]*timeticket[a-z0-9.-]*/[^\s]+",
    r"https?://[a-z0-9.-]*entradas[a-z0-9.-]*/[^\s]+",
    r"https?://bit\.ly/[a-zA-Z0-9]+",
]


def extract_urls(text):
    """Extract all URLs from text."""
    if not text:
        return []
    urls = []
    for pattern in TICKET_PATTERNS:
        urls.extend(re.findall(pattern, text, re.IGNORECASE))
    return urls


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    updates = []
    for i, r in enumerate(rows, 2):
        if len(r) < 12:
            continue

        caption = (r[7] or "").strip()
        status = (r[11] or "").strip() if len(r) > 11 else ""

        if status != "pending" or not caption:
            continue

        # Check if caption already has ticket link
        if "Entradas:" in caption or "entradas:" in caption:
            continue

        urls = extract_urls(caption)
        if urls:
            # Take first URL (most likely the main ticket link)
            ticket_url = urls[0]
            new_caption = f"{caption}\n\nEntradas: {ticket_url}"
            updates.append({
                "row": i,
                "url": ticket_url,
                "new_caption": new_caption,
            })
            print(f"  Fila {i}: Found ticket link")

    if not updates:
        print("Sin enlaces de tickets en captions pendientes")
        return 0

    print(f"\n→ {len(updates)} posts con enlaces encontrados")

    if args.apply:
        batch_updates = []
        for upd in updates:
            batch_updates.append({
                "range": f"Queue!H{upd['row']}",
                "values": [[upd["new_caption"]]]
            })
        if batch_updates:
            sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=sid,
                body={"valueInputOption": "RAW", "data": batch_updates}).execute()
            print(f"✓ Actualizados {len(updates)} captions")

    return 0


if __name__ == "__main__":
    sys.exit(main())
