#!/usr/bin/env python3
"""
Scrape upcoming electronic music events from Passline (passline.com).

Passline is behind Cloudflare bot protection — direct requests return 403.
This scraper uses Firecrawl to render the page and extract events.

Requires:
  FIRECRAWL_API_KEY in .env

Target URL:
  https://passline.com/eventos/musica-electronica

Usage:
  python3 tools/scrape_passline.py
  python3 tools/scrape_passline.py --days 45 --output .tmp/passline_events.json
"""

import argparse
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "").strip()
FIRECRAWL_SCRAPE = "https://api.firecrawl.dev/v1/scrape"
PASSLINE_BASE = "https://passline.com"
PASSLINE_ELECTRONIC = f"{PASSLINE_BASE}/eventos/musica-electronica"


def firecrawl_scrape(url: str) -> dict:
    """Scrape a URL via Firecrawl, return both markdown and raw HTML."""
    resp = requests.post(
        FIRECRAWL_SCRAPE,
        json={
            "url": url,
            "formats": ["markdown", "html"],
            "onlyMainContent": True,
            "waitFor": 2000,
        },
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=40,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def parse_events_from_markdown(markdown: str, cutoff_date: str) -> list[dict]:
    """
    Parse event listings from Firecrawl markdown output.
    Passline event cards typically contain: title, date, venue, city, price, image, link.
    This parser uses regex heuristics — update patterns if Passline changes its layout.
    """
    events = []
    # Split into blocks by horizontal rule or double newline patterns that separate cards
    # Passline markdown typically renders each event as a heading + metadata block
    blocks = re.split(r"\n#{1,3} ", markdown)

    for block in blocks:
        if not block.strip():
            continue

        # Skip blocks that clearly aren't events
        lower = block.lower()
        if not any(kw in lower for kw in ["entrada", "ticket", "fecha", "venue", "evento", "fiesta", "club", "$"]):
            continue

        # Extract title (first line of block, or after the heading marker)
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        title = lines[0].lstrip("#").strip()

        # Skip navigation/filter items that are too short
        if len(title) < 5:
            continue

        # Extract date — common Passline format: "Sáb 28 Jun" or "28/06/2025" or "2025-06-28"
        date_str = ""
        date_match = re.search(
            r"(\d{4}-\d{2}-\d{2})"                        # ISO
            r"|(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})"    # DD/MM/YYYY
            r"|((?:lun|mar|mié|jue|vie|sáb|sab|dom)\w*\s+\d{1,2}\s+\w+)",  # Sáb 28 Jun
            block, re.IGNORECASE,
        )
        if date_match:
            raw_date = (date_match.group(1) or date_match.group(2) or date_match.group(3) or "").strip()
            date_str = normalise_date(raw_date)

        # Skip past events if we have a date and it's before cutoff
        if date_str and date_str < cutoff_date:
            continue

        # Extract venue and city (lines mentioning location keywords)
        venue = ""
        city = ""
        for line in lines[1:]:
            ll = line.lower()
            if any(kw in ll for kw in ["club", "teatro", "estadio", "arena", "espacio", "galpón", "boliche", "venue"]):
                venue = line.strip("- •|").strip()
                break
        for line in lines[1:]:
            ll = line.lower()
            if any(kw in ll for kw in ["buenos aires", "córdoba", "rosario", "mendoza", "la plata", "mar del plata"]):
                city = line.strip("- •|").strip()
                break
        if not city:
            city = "Buenos Aires"  # default — most Passline electronic events are BA

        # Extract image URL
        img_url = ""
        img_match = re.search(r"!\[.*?\]\((https?://[^)]+)\)", block)
        if img_match:
            img_url = img_match.group(1)

        # Extract event link
        event_url = ""
        link_match = re.search(r"\[.*?\]\((https?://passline\.com/evento[^)]+)\)", block)
        if link_match:
            event_url = link_match.group(1)

        # Extract artists (lines that look like artist names — capitalised words, after a "con:" or "artistas:" marker)
        artists = []
        artist_match = re.search(r"(?:con|artistas?|lineup|djs?)[:\s]+([^\n]+)", block, re.IGNORECASE)
        if artist_match:
            raw = artist_match.group(1)
            artists = [a.strip() for a in re.split(r"[,+/|•]", raw) if a.strip() and len(a.strip()) > 1]

        events.append({
            "name": title,
            "date": date_str,
            "time": "",
            "venue": venue,
            "city": city,
            "artists": artists,
            "image_url": img_url,
            "event_url": event_url or PASSLINE_ELECTRONIC,
        })

    return events


def normalise_date(raw: str) -> str:
    """Convert various date formats to YYYY-MM-DD. Returns '' on failure."""
    import calendar

    raw = raw.strip()

    # ISO already
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return raw

    # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    m = re.match(r"^(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})$", raw)
    if m:
        d, mo, y = m.group(1), m.group(2), m.group(3)
        if len(y) == 2:
            y = "20" + y
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

    # Spanish "Sáb 28 Jun" or "28 Jun 2025"
    month_map = {
        "ene": "01", "feb": "02", "mar": "03", "abr": "04",
        "may": "05", "jun": "06", "jul": "07", "ago": "08",
        "sep": "09", "oct": "10", "nov": "11", "dic": "12",
        "jan": "01", "feb": "02", "apr": "04", "aug": "08",
        "dec": "12",
    }
    m2 = re.search(r"(\d{1,2})\s+(\w{3})\w*\s*(\d{4})?", raw, re.IGNORECASE)
    if m2:
        d = m2.group(1).zfill(2)
        mon = month_map.get(m2.group(2).lower()[:3], "")
        y = m2.group(3) or str(date.today().year)
        if mon:
            return f"{y}-{mon}-{d}"

    return ""


def scrape_events(days: int = 45) -> list[dict]:
    if not FIRECRAWL_API_KEY:
        print("ERROR: FIRECRAWL_API_KEY not set in .env")
        return []

    cutoff = date.today().isoformat()
    horizon = (date.today() + timedelta(days=days)).isoformat()

    print(f"Fetching Passline electronic events via Firecrawl...")
    try:
        page_data = firecrawl_scrape(PASSLINE_ELECTRONIC)
    except requests.RequestException as e:
        print(f"  ERROR: Firecrawl request failed: {e}")
        return []

    markdown = page_data.get("markdown", "")
    if not markdown:
        print("  WARN: Firecrawl returned empty markdown — page may have changed structure")
        return []

    print(f"  Got {len(markdown)} chars of markdown")
    events = parse_events_from_markdown(markdown, cutoff)

    # Filter to within our date horizon
    filtered = [e for e in events if not e["date"] or e["date"] <= horizon]

    return filtered


def main():
    parser = argparse.ArgumentParser(description="Scrape Passline electronic events via Firecrawl")
    parser.add_argument("--days", type=int, default=45, help="Days ahead to look")
    parser.add_argument("--output", default=".tmp/passline_events.json")
    args = parser.parse_args()

    os.makedirs(".tmp", exist_ok=True)

    events = scrape_events(days=args.days)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(events)} events → {args.output}")
    for e in events:
        artists = ", ".join(e["artists"][:2]) or "TBC"
        print(f"  {e['date']} — {e['name']} @ {e['venue']} [{artists}]")


if __name__ == "__main__":
    main()
