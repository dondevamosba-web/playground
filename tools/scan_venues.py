#!/usr/bin/env python3
"""
Scan venue/promoter IG accounts for flyers and news worth reposting to Fiestas.

Uses the Graph API business_discovery endpoint. The unofficial web_profile_info
endpoint that auto_fiestas_queue.py relies on started returning 429 in July 2026,
so this is the working path for reading other accounts.

Drops recaps, thank-you posts and anything whose event date has passed, then
dedupes against the Queue tab so an event already in the sheet never comes back.
Writes candidates to JSON for review — captions are written by hand, since
tools/claude_call.py has no working auth on this machine.

Usage:
  python3 tools/scan_venues.py
  python3 tools/scan_venues.py --handles crobarclub clubthebowba
  python3 tools/scan_venues.py --limit 25 --out .tmp/candidates.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import requests
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

# Venue and promoter accounts. Unlike auto_fiestas_queue.IG_SOURCES these are the
# places that announce their own dates, so a post here is usually a real flyer.
VENUE_SOURCES = [
    "bantalent",
    "mandarineparkoficial",
    "crobarclub",
    "clubthebowba",
    "pmopenair",
    "rioelectronicmusic",
    "creamfieldsargentina",
    "brigadocrew",
    "elementsba",
    "mushroom_arg",
    "desertinme",
    "estamosfelices",
]

FIELDS = ("business_discovery.username({h})"
          "{{followers_count,media.limit({n}){{media_type,media_product_type,caption,"
          "permalink,timestamp,like_count,media_url,thumbnail_url,"
          "children{{media_url,media_type}}}}}}")

# Recaps and thank-yous look like event posts to a keyword filter but point backwards.
RECAP_KW = re.compile(
    r"\b(qué bien la pasamos|que bien la pasamos|gracias por venir|gracias por hacerlo|"
    r"así fue|asi fue|recap|seguimos disfrutando|lo que nos dejó|lo que nos dejo|"
    r"registros x|qué debut|que debut|qué manera de bailar|que manera de bailar|"
    r"nos vemos pronto|volvimos de|se vivió|se vivio)\b",
    re.IGNORECASE,
)

MONTHS = {m: i + 1 for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre "
    "noviembre diciembre".split())}

DAY_MONTH = re.compile(
    r"\b(\d{1,2})\s*(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|octubre|noviembre|diciembre)\b", re.IGNORECASE)
NUMERIC = re.compile(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b")

WEEKDAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
WEEKDAY_RE = re.compile(
    r"\b(lunes|martes|mi[ée]rcoles|jueves|viernes|s[áa]bado|domingo)\b", re.IGNORECASE)


def event_date(caption: str, posted: date) -> str | None:
    """Best-effort event date from a caption, rolled forward to the next occurrence."""
    m = DAY_MONTH.search(caption)
    if m:
        day, month = int(m.group(1)), MONTHS[m.group(2).lower()]
    else:
        m = NUMERIC.search(caption)
        if not m:
            return None
        day, month = int(m.group(1)), int(m.group(2))
        if month > 12:
            return None
    for year in (posted.year, posted.year + 1):
        try:
            cand = date(year, month, day)
        except ValueError:
            return None
        if cand >= posted:
            return cand.isoformat()
    return None


def weekday_conflict(caption: str, ev: str) -> str | None:
    """Return a warning when the caption names a weekday the date does not fall on.

    Venues do get this wrong, and a flyer for a night that already happened is
    the one mistake worth catching before it reaches the queue.
    """
    m = WEEKDAY_RE.search(caption)
    if not m:
        return None
    said = m.group(1).lower().replace("miercoles", "miércoles").replace("sabado", "sábado")
    actual = WEEKDAYS[date.fromisoformat(ev).weekday()]
    return f'dice "{said}" pero {ev} es {actual}' if said != actual else None


def best_image(m: dict) -> str:
    """Pick a usable still: first image of a carousel, else the media or thumbnail."""
    if m.get("media_type") == "CAROUSEL_ALBUM":
        for kid in m.get("children", {}).get("data", []):
            if kid.get("media_type") == "IMAGE" and kid.get("media_url"):
                return kid["media_url"]
    if m.get("media_type") == "VIDEO":
        return m.get("thumbnail_url", "")
    return m.get("media_url") or m.get("thumbnail_url") or ""


def known_shortcodes(sheets, sheet_id: str) -> set:
    """Shortcodes already in the Queue tab, from both the name and source-url columns."""
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Queue!A2:N1000").execute().get("values", [])
    seen = set()
    for r in rows:
        if len(r) > 2 and r[2].strip():
            seen.add(r[2].strip())
        if len(r) > 10 and r[10].strip():
            m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", r[10])
            if m:
                seen.add(m.group(1))
    return seen


def scan(handle: str, limit: int, token: str, ig_id: str) -> tuple[list[dict], int]:
    r = requests.get(f"https://graph.facebook.com/v21.0/{ig_id}",
                     params={"fields": FIELDS.format(h=handle, n=limit),
                             "access_token": token}, timeout=30).json()
    if "error" in r:
        print(f"  @{handle}: ERROR {r['error'].get('message', '')[:110]}")
        return [], 0
    bd = r["business_discovery"]
    media = bd.get("media", {}).get("data", [])
    out = []
    for m in media:
        caption = m.get("caption") or ""
        if RECAP_KW.search(caption):
            continue
        posted = date.fromisoformat(m["timestamp"][:10])
        ev = event_date(caption, posted)
        if not ev or date.fromisoformat(ev) < date.today():
            continue
        img = best_image(m)
        if not img:
            continue
        out.append({
            "handle": handle,
            "followers": bd.get("followers_count", 0),
            "shortcode": m["permalink"].rstrip("/").split("/")[-1],
            "permalink": m["permalink"],
            "posted": m["timestamp"][:10],
            "event_date": ev,
            "warning": weekday_conflict(caption, ev),
            "likes": m.get("like_count", 0),
            "media_type": m["media_type"],
            "caption": caption,
            "image_url": img,
        })
    return out, len(media)


def load_trending_artists():
    """Load trending artist scores from prediction_trending.json."""
    pred_file = ROOT / ".tmp" / "prediction_trending.json"
    if not pred_file.exists():
        # Try to generate it
        try:
            subprocess.run([sys.executable, "tools/predict_trending.py"],
                          capture_output=True, timeout=120, cwd=ROOT)
        except Exception:
            pass

    if pred_file.exists():
        try:
            data = json.loads(pred_file.read_text(encoding="utf-8"))
            # Return list of top artists for quick lookup
            return [a[0] for a in data.get("top_artists", [])][:20]
        except Exception:
            pass
    return []


def score_candidate(candidate, trending_artists):
    """Score a candidate by how trending the artist is."""
    name = candidate["caption"].split("\n")[0].lower()

    # If artist is in top trending, boost score
    for i, artist in enumerate(trending_artists):
        if artist.lower() in name:
            return 1000 - i  # Higher score for top artistas

    return 0  # No trend score


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--handles", nargs="+", default=VENUE_SOURCES)
    p.add_argument("--limit", type=int, default=15, help="Posts to pull per account")
    p.add_argument("--out", default=str(ROOT / ".tmp" / "venue_candidates.json"))
    p.add_argument("--no-dedupe", action="store_true",
                   help="Skip the Queue-tab check (useful when testing filters)")
    args = p.parse_args()

    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
    ig_id = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]

    seen = set()
    if not args.no_dedupe:
        sheets, _ = get_services()
        seen = known_shortcodes(sheets, os.environ["FIESTAS_APPROVAL_SHEET_ID"])
        print(f"Queue: {len(seen)} shortcodes conocidos\n")

    candidates = []
    for handle in args.handles:
        found, total = scan(handle, args.limit, token, ig_id)
        fresh = [c for c in found if c["shortcode"] not in seen]
        candidates += fresh
        print(f"  @{handle}: {len(fresh)} candidatos de {total} posts")

    # Score by trending artists
    trending = load_trending_artists()
    for c in candidates:
        c["trend_score"] = score_candidate(c, trending)

    # Sort by: trending score (DESC) then event date (ASC)
    candidates.sort(key=lambda c: (-c["trend_score"], c["event_date"]))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"\n{len(candidates)} candidatos -> {out_path}\n")
    for c in candidates:
        head = c["caption"].split("\n")[0][:70]
        trend_emoji = "🔥" if c["trend_score"] > 500 else "📈" if c["trend_score"] > 0 else "  "
        print(f"{trend_emoji} [{c['event_date']}] @{c['handle']:22} {head}")
        if c["warning"]:
            print(f"             ⚠ {c['warning']}")

    if candidates:
        print("\nEscribí los captions y cargá las filas como 'pending'. "
              "Nunca 'approved' sin revisar.")


if __name__ == "__main__":
    main()
