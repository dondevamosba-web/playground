#!/usr/bin/env python3
"""
Export all real Ola Digital artboards from ola-digital-posts.html (root) as PNGs.
Skips the cover/system slide. Mirrors screenshot_storm.py's approach.

Usage:
  python3 tools/screenshot_ola_digital_v2.py
"""
import asyncio
import http.server
import json
import re
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent
HTML_FILE = ROOT / "ola-digital-posts.html"
OUT_DIR = ROOT / ".tmp" / "ola_digital_posts_v2"
PORT = 8802


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


async def export_artboards():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = start_server(ROOT, PORT)
    url = f"http://localhost:{PORT}/ola-digital-posts.html"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 3200, "height": 3200},
                device_scale_factor=1,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            await page.wait_for_selector("[data-dc-slot]", timeout=30_000)
            await asyncio.sleep(3)

            slots = await page.query_selector_all("[data-dc-slot]")
            print(f"Found {len(slots)} artboards")

            saved = []
            for slot in slots:
                slot_id = await slot.get_attribute("data-dc-slot") or ""
                label_el = await slot.query_selector(".dc-labeltext")
                label = (await label_el.inner_text()).strip() if label_el else slot_id

                if "sistema" in label.lower() or "system" in label.lower():
                    print(f"  Skipping cover slide: {label}")
                    continue

                card = await slot.query_selector(".dc-card")
                if not card:
                    print(f"  Skipping {label} — no .dc-card")
                    continue

                fname = safe_filename(label or slot_id) + ".png"
                out_path = OUT_DIR / fname
                print(f"  -> {label}")
                await card.screenshot(path=str(out_path))
                saved.append({"label": label, "id": slot_id, "file": str(out_path)})

            await browser.close()
    finally:
        server.shutdown()

    manifest = OUT_DIR / "_manifest.json"
    manifest.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(saved)} PNGs -> {OUT_DIR}/")
    return saved


if __name__ == "__main__":
    asyncio.run(export_artboards())
