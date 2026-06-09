#!/usr/bin/env python3
"""
Screenshot each artboard from the OLA Digital design canvas at native resolution.
Saves PNGs to .tmp/posts/ ready for Drive upload and Instagram posting.

Usage:
  python tools/screenshot_designs.py
  python tools/screenshot_designs.py --filter feed
  python tools/screenshot_designs.py --filter carousel
  python tools/screenshot_designs.py --filter story
"""

import argparse
import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

DEFAULT_HTML_URL = "http://localhost:8765/OLA%20Digital%20-%20Brand%20Assets.html"
OUT_DIR = Path(__file__).parent.parent / ".tmp" / "posts"


def safe_filename(label: str, max_len: int = 80) -> str:
    s = label.replace(" · ", "_").replace(" ", "_").replace("/", "-").replace(":", "")
    s = re.sub(r"[^\w\-]", "", s).strip("_").lower()
    return s[:max_len]


async def screenshot_artboards(filter_str: str = None, html_url: str = DEFAULT_HTML_URL):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 3000, "height": 3000},
            device_scale_factor=1,
        )
        page = await context.new_page()

        print(f"Loading: {html_url}")
        await page.goto(html_url, wait_until="networkidle", timeout=60000)

        # Wait for React to render artboards
        await page.wait_for_selector("[data-dc-slot]", timeout=30000)
        await asyncio.sleep(3)  # let animations + fonts settle

        slots = await page.query_selector_all("[data-dc-slot]")
        print(f"Found {len(slots)} artboards")

        saved = []
        for slot in slots:
            slot_id = await slot.get_attribute("data-dc-slot")

            # Get label from the header text
            label_el = await slot.query_selector(".dc-labeltext")
            label = (await label_el.inner_text()).strip() if label_el else slot_id

            if filter_str and filter_str.lower() not in (slot_id or "").lower() and filter_str.lower() not in label.lower():
                continue

            # Screenshot the card (the actual artboard content, no header)
            card = await slot.query_selector(".dc-card")
            if not card:
                print(f"  Skipping {label} — no .dc-card found")
                continue

            fname = safe_filename(label) + ".png"
            out_path = OUT_DIR / fname

            print(f"  → {label}")
            await card.screenshot(path=str(out_path))
            saved.append({"label": label, "id": slot_id, "file": str(out_path)})

        await browser.close()

        manifest_path = OUT_DIR / "_manifest.json"
        manifest_path.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
        print(f"\nSaved {len(saved)} PNGs to {OUT_DIR}/")
        return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Only artboards matching this string (e.g. feed, carousel, story, logo, reel)")
    parser.add_argument("--html", default=DEFAULT_HTML_URL, help="URL of the HTML design canvas to screenshot")
    args = parser.parse_args()
    asyncio.run(screenshot_artboards(args.filter, html_url=args.html))


if __name__ == "__main__":
    main()
