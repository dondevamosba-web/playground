#!/usr/bin/env python3
"""
Export the real Storm Digital post kit from brand-toolkit/storm-posts/*.html
(50 individually-designed posts) as PNGs. This is the rich-content source —
NOT the same as root storm-digital-posts.html, which only has placeholder copy.

Usage:
  python3 tools/screenshot_storm_v2.py
"""
import asyncio
import http.server
import re
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "brand-toolkit" / "storm-posts"
OUT_DIR = ROOT / ".tmp" / "storm_posts_v2"
PORT = 8803


def safe_filename(stem: str) -> str:
    s = re.sub(r"[^\w\-]", "_", stem).strip("_").lower()
    return s


def start_server(directory: Path, port: int) -> http.server.HTTPServer:
    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("localhost", port), SilentHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


async def export_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = start_server(SRC_DIR, PORT)

    html_files = sorted(SRC_DIR.glob("*.html"))
    print(f"Found {len(html_files)} post files")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 1200, "height": 1200},
                device_scale_factor=1,
            )
            page = await context.new_page()

            for f in html_files:
                url = f"http://localhost:{PORT}/{f.name}"
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                await asyncio.sleep(0.6)
                card = await page.query_selector(".post")
                if not card:
                    print(f"  SKIP {f.name} — no .post element")
                    continue
                out_path = OUT_DIR / (safe_filename(f.stem) + ".png")
                await card.screenshot(path=str(out_path))
                print(f"  -> {f.stem}")

            await browser.close()
    finally:
        server.shutdown()

    print(f"\nSaved PNGs -> {OUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(export_all())
