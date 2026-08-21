#!/usr/bin/env python3
"""
Export all Storm Digital artboards from storm-digital-posts.html as PNGs.
Serves the HTML locally via HTTP, uses Playwright to screenshot each .dc-card.

Usage:
  python tools/screenshot_storm.py                    # export all 40 posts
  python tools/screenshot_storm.py --filter single    # singles only
  python tools/screenshot_storm.py --filter carousel  # carousels only
  python tools/screenshot_storm.py --out /custom/dir  # custom output dir
"""

import argparse
import asyncio
import http.server
import json
import re
import subprocess
import sys
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "storm-digital-posts.html"
OUT_DIR = ROOT / ".tmp" / "storm_posts"
PORT = 8766


def safe_filename(label: str, max_len: int = 80) -> str:
    s = label.replace(" · ", "_").replace(" ", "_").replace("/", "-").replace(":", "")
    s = re.sub(r"[^\w\-]", "", s).strip("_").lower()
    return s[:max_len]


def start_server(directory: Path, port: int) -> http.server.HTTPServer:
    handler = http.server.SimpleHTTPRequestHandler
    handler.directory = str(directory)

    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format, *args):
            pass  # suppress access logs

    server = http.server.HTTPServer(("localhost", port), SilentHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


async def export_artboards(filter_str: str | None, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    server = start_server(ROOT, PORT)
    url = f"http://localhost:{PORT}/storm-digital-posts.html"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 3200, "height": 3200},
                device_scale_factor=1,
            )
            page = await context.new_page()

            print(f"Loading: {url}")
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            await page.wait_for_selector("[data-dc-slot]", timeout=30_000)
            await asyncio.sleep(3)  # fonts + animations settle

            slots = await page.query_selector_all("[data-dc-slot]")
            print(f"Found {len(slots)} artboards")

            saved = []
            for slot in slots:
                slot_id = await slot.get_attribute("data-dc-slot") or ""
                label_el = await slot.query_selector(".dc-labeltext")
                label = (await label_el.inner_text()).strip() if label_el else slot_id

                if filter_str and (
                    filter_str.lower() not in slot_id.lower()
                    and filter_str.lower() not in label.lower()
                ):
                    continue

                card = await slot.query_selector(".dc-card")
                if not card:
                    print(f"  Skipping {label} — no .dc-card")
                    continue

                fname = safe_filename(label or slot_id) + ".png"
                out_path = out_dir / fname

                print(f"  → {label}")
                await card.screenshot(path=str(out_path))
                saved.append({"label": label, "id": slot_id, "file": str(out_path)})

            await browser.close()

    finally:
        server.shutdown()

    manifest = out_dir / "_manifest.json"
    manifest.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    print(f"\n✓ Saved {len(saved)} PNGs → {out_dir}/")
    return saved


def main():
    parser = argparse.ArgumentParser(description="Export Storm Digital posts as PNGs")
    parser.add_argument("--filter", help="Only artboards whose id or label contains this string")
    parser.add_argument("--out", type=Path, default=OUT_DIR, help="Output directory")
    args = parser.parse_args()

    asyncio.run(export_artboards(args.filter, args.out))

    # Auto-generate story versions (1080x1920) alongside the feed PNGs
    import subprocess
    subprocess.run([
        sys.executable, str(ROOT / "tools" / "make_story_versions.py"),
        "--dir", str(args.out),
        "--bg", "#0c0817",
        "--skip-existing",
    ])


if __name__ == "__main__":
    main()
