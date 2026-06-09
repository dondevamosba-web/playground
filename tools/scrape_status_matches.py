"""
Scrapes loyalty status match opportunities for Lufthansa Senator + SAS EuroBonus Gold.
Both are Star Alliance Gold equivalent — opens matches across hotels, airlines, and car rentals.

Sources:
  1. StatusMatcher.com — community-tracked match offers
  2. Curated list of known ongoing matches (updated as discovered)

Caches results in .tmp/status_matches_seen.json to surface only NEW offers.

Usage:
  python3 tools/scrape_status_matches.py             # check and draft if new
  python3 tools/scrape_status_matches.py --force     # draft even if no new offers
  python3 tools/scrape_status_matches.py --dry-run   # print without drafting
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from tools.gmail_draft import create_draft

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "status_matches_seen.json")
RECIPIENT = "dondevamosba@gmail.com"

# Your current statuses and their equivalences
MY_STATUSES = [
    {"program": "Lufthansa Miles & More", "tier": "Senator", "alliance": "Star Alliance Gold"},
    {"program": "SAS EuroBonus", "tier": "Gold", "alliance": "Star Alliance Gold"},
]

# Known ongoing match offers — curated baseline (update as new offers are discovered)
# Format: {id, category, from_status, to_program, to_tier, type, url, notes, expires}
KNOWN_OFFERS = [
    # ── HOTELS ──────────────────────────────────────────────────────────────────
    {
        "id": "marriott-star-alliance-gold",
        "category": "Hotel",
        "from_status": "Star Alliance Gold",
        "to_program": "Marriott Bonvoy",
        "to_tier": "Gold Elite",
        "type": "Status Match",
        "url": "https://www.marriott.com/loyalty/statusMatch.mi",
        "notes": "Ongoing: Star Alliance Gold → Marriott Gold Elite. Valid for 90 days, extendable with 4 stays.",
        "expires": "ongoing",
    },
    {
        "id": "hilton-lufthansa-senator",
        "category": "Hotel",
        "from_status": "Lufthansa Senator",
        "to_program": "Hilton Honors",
        "to_tier": "Gold",
        "type": "Status Match",
        "url": "https://www.hilton.com/en/hilton-honors/partner-airlines/",
        "notes": "Lufthansa Senator → Hilton Gold via Miles & More partnership. Check Hilton–Miles & More page.",
        "expires": "ongoing",
    },
    {
        "id": "ihg-star-alliance",
        "category": "Hotel",
        "from_status": "Star Alliance Gold",
        "to_program": "IHG One Rewards",
        "to_tier": "Platinum Elite",
        "type": "Status Match",
        "url": "https://www.ihg.com/rewardsclub/content/us/en/statusmatch",
        "notes": "IHG periodically offers Star Alliance Gold → Platinum Elite. Check current availability.",
        "expires": "periodic",
    },
    {
        "id": "radisson-star-alliance",
        "category": "Hotel",
        "from_status": "Star Alliance Gold",
        "to_program": "Radisson Rewards",
        "to_tier": "Gold",
        "type": "Status Match",
        "url": "https://www.radissonhotels.com/en-us/rewards",
        "notes": "Radisson has offered Star Alliance Gold matches. Check their status match page.",
        "expires": "periodic",
    },
    # ── CAR RENTALS ─────────────────────────────────────────────────────────────
    {
        "id": "hertz-star-alliance",
        "category": "Car Rental",
        "from_status": "Star Alliance Gold",
        "to_program": "Hertz Gold Plus Rewards",
        "to_tier": "Five Star",
        "type": "Status Match",
        "url": "https://www.hertz.com/rentacar/misc/index.jsp?targetPage=starAlliance.jsp",
        "notes": "Hertz Five Star via Star Alliance Gold. Includes free upgrades and car class guarantees.",
        "expires": "ongoing",
    },
    {
        "id": "avis-star-alliance",
        "category": "Car Rental",
        "from_status": "Star Alliance Gold",
        "to_program": "Avis Preferred",
        "to_tier": "Preferred Plus",
        "type": "Status Match",
        "url": "https://www.avis.com/en/members/avis-preferred/star-alliance",
        "notes": "Avis Preferred Plus via Star Alliance Gold membership.",
        "expires": "ongoing",
    },
    {
        "id": "sixt-lufthansa",
        "category": "Car Rental",
        "from_status": "Lufthansa Senator",
        "to_program": "Sixt",
        "to_tier": "Platinum",
        "type": "Status Match",
        "url": "https://www.sixt.com/service/lufthansa/",
        "notes": "Lufthansa Miles & More Senator → Sixt Platinum via LH partnership. Free upgrades.",
        "expires": "ongoing",
    },
    {
        "id": "budget-star-alliance",
        "category": "Car Rental",
        "from_status": "Star Alliance Gold",
        "to_program": "Budget Fastbreak",
        "to_tier": "Business",
        "type": "Status Match",
        "url": "https://www.budget.com/en/programs/star-alliance",
        "notes": "Budget Fastbreak Business tier via Star Alliance Gold.",
        "expires": "ongoing",
    },
    # ── AIRLINES ────────────────────────────────────────────────────────────────
    {
        "id": "tap-star-alliance-challenge",
        "category": "Airline",
        "from_status": "Star Alliance Gold",
        "to_program": "TAP Miles&Go",
        "to_tier": "Gold",
        "type": "Status Challenge",
        "url": "https://www.flytap.com/en-us/miles-and-go/status/status-match",
        "notes": "TAP periodically offers Star Alliance Gold status challenges. Worth checking.",
        "expires": "periodic",
    },
    {
        "id": "aegean-star-alliance",
        "category": "Airline",
        "from_status": "Star Alliance Gold",
        "to_program": "Aegean Miles+Bonus",
        "to_tier": "Gold",
        "type": "Status Match",
        "url": "https://www.aegeanair.com/en/miles-bonus/members/status-match/",
        "notes": "Aegean has offered direct Star Alliance Gold matches. Check current page.",
        "expires": "periodic",
    },
]


def _fetch(url: str, timeout: int = 15) -> str:
    """Fetch a URL and return the HTML body."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"


def scrape_statusmatcher(program_keyword: str) -> list[dict]:
    """
    Fetches StatusMatcher.com search results for a given program keyword.
    Returns list of match snippets found.
    """
    encoded = urllib.parse.quote(program_keyword)
    url = f"https://www.statusmatcher.com/search?q={encoded}"
    html = _fetch(url)
    if html.startswith("ERROR"):
        return []

    # Extract match entries — StatusMatcher uses simple card/list structure
    matches = []
    # Look for patterns like "X → Y" or program names in result blocks
    entries = re.findall(
        r'class="[^"]*match[^"]*"[^>]*>(.*?)</(?:div|li|article)>',
        html, re.DOTALL | re.IGNORECASE
    )
    for entry in entries[:10]:
        clean = re.sub(r"<[^>]+>", " ", entry).strip()
        clean = re.sub(r"\s+", " ", clean)
        if len(clean) > 20:
            matches.append({"source": "statusmatcher.com", "snippet": clean[:300]})

    # Also try to catch any structured data or JSON-LD
    json_ld = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for block in json_ld:
        try:
            data = json.loads(block)
            if isinstance(data, dict) and data.get("name"):
                matches.append({"source": "statusmatcher.com/ld", "snippet": str(data)[:300]})
        except Exception:
            pass

    return matches


def load_cache() -> dict:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {"seen_ids": [], "last_run": None}


def save_cache(cache: dict):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def find_new_offers(cache: dict) -> list[dict]:
    seen = set(cache.get("seen_ids", []))
    return [o for o in KNOWN_OFFERS if o["id"] not in seen]


def build_html_report(new_offers: list[dict], all_offers: list[dict], statusmatcher_results: list[dict]) -> str:
    today = date.today().strftime("%B %d, %Y")

    categories = {}
    for offer in all_offers:
        categories.setdefault(offer["category"], []).append(offer)

    new_ids = {o["id"] for o in new_offers}

    sections_html = ""
    cat_icons = {"Hotel": "🏨", "Car Rental": "🚗", "Airline": "✈️"}

    for cat, offers in categories.items():
        icon = cat_icons.get(cat, "")
        rows = ""
        for o in offers:
            is_new = o["id"] in new_ids
            badge = '<span style="background:#16a34a;color:#fff;font-size:11px;padding:2px 7px;border-radius:9px;margin-left:8px;font-weight:600;">NEW</span>' if is_new else ""
            expiry_color = "#ef4444" if o["expires"] not in ("ongoing", "periodic") else "#6b7280"
            rows += f"""
            <tr style="border-bottom:1px solid #f3f4f6;">
              <td style="padding:10px 12px;font-weight:600;font-size:14px;">{o['to_program']}{badge}</td>
              <td style="padding:10px 12px;font-size:13px;color:#374151;">{o['to_tier']}</td>
              <td style="padding:10px 12px;font-size:12px;color:#6b7280;">{o['from_status']}</td>
              <td style="padding:10px 12px;font-size:12px;color:{expiry_color};">{o['expires']}</td>
              <td style="padding:10px 12px;font-size:12px;">
                <a href="{o['url']}" style="color:#2563eb;">Apply →</a>
              </td>
            </tr>
            <tr>
              <td colspan="5" style="padding:4px 12px 12px;font-size:12px;color:#6b7280;font-style:italic;">{o['notes']}</td>
            </tr>"""

        sections_html += f"""
        <h3 style="margin:24px 0 8px;font-size:15px;font-weight:700;color:#0E1116;">{icon} {cat}</h3>
        <table style="width:100%;border-collapse:collapse;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb;">
          <thead>
            <tr style="background:#f9fafb;">
              <th style="padding:8px 12px;text-align:left;font-weight:600;color:#374151;">Program</th>
              <th style="padding:8px 12px;text-align:left;font-weight:600;color:#374151;">Target Tier</th>
              <th style="padding:8px 12px;text-align:left;font-weight:600;color:#374151;">From Status</th>
              <th style="padding:8px 12px;text-align:left;font-weight:600;color:#374151;">Expires</th>
              <th style="padding:8px 12px;text-align:left;font-weight:600;color:#374151;">Link</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>"""

    sm_section = ""
    if statusmatcher_results:
        snippets = "".join(
            f'<li style="margin-bottom:6px;font-size:13px;color:#374151;">{r["snippet"]}</li>'
            for r in statusmatcher_results[:5]
        )
        sm_section = f"""
        <h3 style="margin:24px 0 8px;font-size:15px;font-weight:700;color:#0E1116;">🔍 StatusMatcher.com Live Finds</h3>
        <ul style="padding-left:20px;margin:0;">{snippets}</ul>"""

    new_banner = ""
    if new_offers:
        new_banner = f"""
        <div style="background:#dcfce7;border:1px solid #16a34a;border-radius:8px;padding:12px 16px;margin-bottom:20px;">
          <strong style="color:#15803d;">🎯 {len(new_offers)} new offer(s) since last check</strong>
          <ul style="margin:6px 0 0;padding-left:18px;">
            {''.join(f"<li style='font-size:13px;color:#166534;'>{o['to_program']} — {o['to_tier']} ({o['type']})</li>" for o in new_offers)}
          </ul>
        </div>"""

    return f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;line-height:1.6;color:#0E1116;max-width:700px;">
  <h2 style="margin:0 0 4px;font-size:18px;">Loyalty Status Match Opportunities</h2>
  <p style="margin:0 0 20px;font-size:13px;color:#6b7280;">
    Week of {today} &nbsp;·&nbsp; Based on: Lufthansa Senator + SAS EuroBonus Gold (both = Star Alliance Gold)
  </p>
  {new_banner}
  {sections_html}
  {sm_section}
  <p style="margin-top:24px;font-size:12px;color:#9ca3af;">
    Verify offer availability directly on each program's website before applying — terms change frequently.<br>
    Update <code>KNOWN_OFFERS</code> in <code>tools/scrape_status_matches.py</code> as new offers are found.
  </p>
</div>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Draft even if no new offers")
    parser.add_argument("--dry-run", action="store_true", help="Print HTML, don't draft")
    args = parser.parse_args()

    cache = load_cache()
    new_offers = find_new_offers(cache)

    # Scrape StatusMatcher.com for live community data
    print("Scraping StatusMatcher.com for Lufthansa + SAS...")
    sm_results = []
    for keyword in ["Lufthansa Senator", "SAS EuroBonus Gold"]:
        sm_results.extend(scrape_statusmatcher(keyword))
        time.sleep(1)

    if not new_offers and not args.force:
        print(f"No new offers since last run ({cache.get('last_run', 'never')}). Use --force to send anyway.")
        return

    html = build_html_report(new_offers, KNOWN_OFFERS, sm_results)

    if args.dry_run:
        print(html)
        return

    subject = f"Loyalty Status Match Report — {date.today().strftime('%b %d')}"
    if new_offers:
        subject = f"🎯 {len(new_offers)} New Status Match Offer(s) — {date.today().strftime('%b %d')}"

    result = create_draft(to=RECIPIENT, subject=subject, body=html, html=True)
    print(f"Draft created: {result}")

    # Update cache — mark all current known offers as seen
    cache["seen_ids"] = [o["id"] for o in KNOWN_OFFERS]
    cache["last_run"] = datetime.now().isoformat()
    save_cache(cache)
    print(f"Cache updated. {len(new_offers)} new offers marked as seen.")


if __name__ == "__main__":
    main()
