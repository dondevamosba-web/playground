#!/usr/bin/env python3
"""
Export all Empleo post artboards from ola-empleo-posts.html (root) as PNGs.
Mirrors screenshot_ola_digital_v2.py's approach but targets `.post` divs
with adjacent `.label` text for naming (no data-dc-slot markup here).

Usage:
  python3 tools/screenshot_ola_empleo.py
"""
import asyncio
import http.server
import json
import re
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "ola-empleo-posts.html"
OUT_DIR = ROOT / ".tmp" / "empleo_posts_v2"
PORT = 8803


def safe_filename(label: str, max_len: int = 80) -> str:
    s = label.replace(" · ", "_").replace(" ", "_").replace("/", "-").replace(":", "")
    s = re.sub(r"[^\w\-]", "", s).strip("_").lower()
    return s[:max_len]


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


async def export_posts():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = start_server(ROOT, PORT)
    url = f"http://localhost:{PORT}/ola-empleo-posts.html"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 1200, "height": 1200},
                device_scale_factor=1,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            await page.wait_for_selector(".post", timeout=30_000)
            await asyncio.sleep(1)

            posts = await page.query_selector_all(".post")
            print(f"Found {len(posts)} posts")

            saved = []
            for i, post in enumerate(posts, start=1):
                label_el = await post.evaluate_handle(
                    "el => el.previousElementSibling"
                )
                label = None
                try:
                    label = await label_el.inner_text()
                except Exception:
                    pass
                label = (label or f"post_{i}").strip()

                fname = f"{i:02d}_" + safe_filename(label) + ".png"
                out_path = OUT_DIR / fname
                print(f"  -> {label}")
                await post.screenshot(path=str(out_path))
                saved.append({"label": label, "n": i, "file": str(out_path)})

            await browser.close()
    finally:
        server.shutdown()

    manifest = OUT_DIR / "_manifest.json"
    manifest.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(saved)} PNGs -> {OUT_DIR}/")
    return saved


if __name__ == "__main__":
    asyncio.run(export_posts())
