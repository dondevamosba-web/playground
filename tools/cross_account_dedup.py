#!/usr/bin/env python3
"""
Cross-account event dedup for the Fiestas pipeline.

The same event often gets queued twice because different sources (RA vs.
different IG accounts) spell it differently ("Miss Monique presenta
Biorhythm" vs. "Miss Monique - Biorhythm", accents dropped, extra words).
Comparing raw strings for exact equality misses these. This module
normalizes name+venue+date into a comparable signature and, when that
doesn't match exactly, falls back to token-overlap similarity on the name
(gated by the event date matching) to catch near-duplicates.

Usage:
    from tools.cross_account_dedup import is_duplicate

    if not is_duplicate(name, venue, date, known_events):
        known_events.append({"name": name, "venue": venue, "date": date})
        # ...queue it
"""

import re
import unicodedata

SIMILARITY_THRESHOLD = 0.6  # token Jaccard overlap on names, at matching date


def normalize(text: str) -> str:
    """Lowercase, strip accents/punctuation, collapse whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_date(date_str: str) -> str:
    """Pull out YYYY-MM-DD if present, else fall back to the normalized raw string."""
    date_str = (date_str or "").strip()
    m = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if m:
        return m.group(1)
    return normalize(date_str)


def _tokens(text: str) -> set:
    return set(normalize(text).split())


def token_similarity(a: str, b: str) -> float:
    """Jaccard similarity between the normalized word-token sets of a and b."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def event_signature(name: str, venue: str = "", date: str = "") -> tuple:
    return (normalize(name), normalize(venue), normalize_date(date))


def is_duplicate(name: str, venue: str, date: str, known_events, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """
    known_events: iterable of dicts with "name"/"venue"/"date" keys (or objects
    with those attributes) already queued/posted.

    1. Exact match on the normalized (name, venue, date) signature -> duplicate.
    2. Otherwise, same normalized date + name token-similarity >= threshold -> duplicate
       (catches same event, differently worded, same day).
    """
    sig = event_signature(name, venue, date)
    norm_date = sig[2]
    norm_name = sig[0]

    for ev in known_events:
        ev_name = ev.get("name", "") if isinstance(ev, dict) else getattr(ev, "name", "")
        ev_venue = ev.get("venue", "") if isinstance(ev, dict) else getattr(ev, "venue", "")
        ev_date = ev.get("date", "") if isinstance(ev, dict) else getattr(ev, "date", "")
        ev_sig = event_signature(ev_name, ev_venue, ev_date)

        if ev_sig == sig:
            return True

        if ev_sig[2] == norm_date and norm_date and token_similarity(norm_name, ev_sig[0]) >= threshold:
            return True

    return False


if __name__ == "__main__":
    # Self-contained smoke test (no network/credentials needed).
    known = [
        {"name": "Miss Monique presenta Biorhythm", "venue": "Mandarine Park", "date": "2026-10-03"},
        {"name": "Techno Boat 2026", "venue": "Puerto Madero", "date": "2026-09-20"},
    ]

    cases = [
        ("Miss Monique presenta Biorhythm", "Mandarine Park", "2026-10-03", True, "exact match"),
        ("Miss Monique - Biorhythm", "Mandarine Park, Punta Carrasco", "2026-10-03", True, "reworded near-dup"),
        ("Techno Boat 2026", "Puerto Madero", "2026-09-20", True, "exact match #2"),
        ("Bresh Fiesta", "Konex", "2026-11-01", False, "unrelated event"),
        ("Miss Monique presenta Biorhythm", "Mandarine Park", "2026-11-15", False, "same name, different date"),
    ]

    failed = 0
    for name, venue, date, expected, label in cases:
        got = is_duplicate(name, venue, date, known)
        status = "OK" if got == expected else "FAIL"
        if got != expected:
            failed += 1
        print(f"[{status}] {label}: is_duplicate={got} (expected {expected})")

    print(f"\n{len(cases) - failed}/{len(cases)} passed")
    raise SystemExit(1 if failed else 0)
