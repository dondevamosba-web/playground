#!/usr/bin/env python3
"""
Render cache for the Fiestas weekend story image.

Rendering the weekend digest is only worth doing again if the underlying
event set changed. This hashes the (name, venue, date) of every event going
into the render; if that hash matches the last cached render, the cached
image path is reused instead of re-rendering.

filter_valid_events() also guards the input: rows can come back from the
Google Sheet with a timestamp accidentally sitting in the Event Name column
(a shifted-row bug elsewhere in the pipeline) — those must not reach the
renderer, so they're detected and dropped here.

Usage:
    from tools.render_cache import filter_valid_events, get_cached_render, save_render

    events = filter_valid_events(events)
    cached = get_cached_render("weekend_story", events)
    if cached:
        image_path = cached
    else:
        image_path = render_weekend_story(events)  # however the story actually gets rendered
        save_render("weekend_story", events, image_path)

NOTE: as of writing, no "weekend story" renderer exists yet in tools/ —
this module is the reusable caching layer for whenever that renderer is
built. See the per-event image path in auto_fiestas_queue.py's
brand_image() for the closest existing thing, which renders one image per
post rather than one digest per weekend and doesn't need this cache (dedup
already stops it from re-rendering the same post twice).
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CACHE_DIR = ROOT / ".tmp" / "render_cache"
CACHE_INDEX = CACHE_DIR / "index.json"

# Matches rows where the Event Name looks like a timestamp instead of a name,
# e.g. "2026-09-14 21:33", "14/09/2026", "2026-09-14T21:33:00".
TIMESTAMP_PATTERNS = [
    re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$"),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}([ ]\d{1,2}:\d{2})?$"),
]


def _looks_like_timestamp(value: str) -> bool:
    value = (value or "").strip()
    if not value:
        return False
    return any(p.match(value) for p in TIMESTAMP_PATTERNS)


def filter_valid_events(events: list) -> list:
    """Drop rows whose Event Name is actually a timestamp (corrupted row)."""
    valid = []
    for ev in events:
        name = ev.get("name", "") if isinstance(ev, dict) else getattr(ev, "name", "")
        if _looks_like_timestamp(name):
            continue
        valid.append(ev)
    return valid


def _events_hash(events: list) -> str:
    """Stable, order-independent hash of the event set's identifying fields."""
    keys = []
    for ev in events:
        get = ev.get if isinstance(ev, dict) else lambda k, d="": getattr(ev, k, d)
        keys.append(json.dumps(
            {"name": get("name", ""), "venue": get("venue", ""), "date": get("date", "")},
            sort_keys=True,
        ))
    return hashlib.sha256("|".join(sorted(keys)).encode("utf-8")).hexdigest()[:16]


def _load_index() -> dict:
    if CACHE_INDEX.exists():
        try:
            return json.loads(CACHE_INDEX.read_text())
        except Exception:
            pass
    return {}


def _save_index(index: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_INDEX.write_text(json.dumps(index, indent=2))


def get_cached_render(cache_name: str, events: list) -> Path | None:
    """Return the cached rendered image path if the event set is unchanged, else None."""
    index = _load_index()
    entry = index.get(cache_name)
    if not entry:
        return None
    if entry.get("hash") != _events_hash(events):
        return None
    path = Path(entry.get("path", ""))
    return path if path.exists() else None


def save_render(cache_name: str, events: list, rendered_path: Path):
    """Record a freshly rendered image against the event set that produced it."""
    index = _load_index()
    index[cache_name] = {"hash": _events_hash(events), "path": str(rendered_path)}
    _save_index(index)


if __name__ == "__main__":
    # Self-contained smoke test (no network/credentials needed).
    import tempfile

    failed = 0

    corrupted = [
        {"name": "2026-09-14 21:33", "venue": "Konex", "date": "2026-09-20"},
        {"name": "Bresh Fiesta", "venue": "Konex", "date": "2026-09-20"},
    ]
    cleaned = filter_valid_events(corrupted)
    ok = len(cleaned) == 1 and cleaned[0]["name"] == "Bresh Fiesta"
    print(f"[{'OK' if ok else 'FAIL'}] filter_valid_events dropped the timestamp row")
    failed += 0 if ok else 1

    events_a = [{"name": "Bresh Fiesta", "venue": "Konex", "date": "2026-09-20"}]
    events_b = [{"name": "Bresh Fiesta", "venue": "Konex", "date": "2026-09-20"}]  # same set, new list
    events_c = [{"name": "Bresh Fiesta", "venue": "Konex", "date": "2026-09-27"}]  # different date

    with tempfile.TemporaryDirectory() as tmp:
        fake_render = Path(tmp) / "story.jpg"
        fake_render.write_bytes(b"fake image bytes")

        cache_name = "smoke_test_weekend_story"
        assert get_cached_render(cache_name, events_a) is None, "cache should be empty before first save"
        save_render(cache_name, events_a, fake_render)

        hit = get_cached_render(cache_name, events_b)
        ok = hit == fake_render
        print(f"[{'OK' if ok else 'FAIL'}] unchanged event set reuses the cached render")
        failed += 0 if ok else 1

        miss = get_cached_render(cache_name, events_c)
        ok = miss is None
        print(f"[{'OK' if ok else 'FAIL'}] changed event set invalidates the cache")
        failed += 0 if ok else 1

        # Clean up the smoke-test entry so it doesn't linger in the real cache index.
        index = _load_index()
        index.pop(cache_name, None)
        _save_index(index)

    print(f"\n{3 - failed}/3 passed")
    raise SystemExit(1 if failed else 0)
