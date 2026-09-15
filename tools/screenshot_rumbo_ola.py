#!/usr/bin/env python3
"""
Export all Rumbo OLA artboards from a downloaded Claude Design HTML as PNGs.

Usage:
  python tools/screenshot_rumbo_ola.py                        # usa archivo por defecto
  python tools/screenshot_rumbo_ola.py --html /path/to/file.html
  python tools/screenshot_rumbo_ola.py --out /custom/dir
"""

import argparse
import asyncio
import http.server
import json
import re
import threading
from pathlib import Path

from playwright.async_api import async_playwright

ROOT     = Path(__file__).parent.parent
OUT_DIR  = ROOT / ".tmp" / "rumbo_ola_posts"
PORT     = 8769

DEFAULT_HTML = ROOT / "Rumbo OLA Kit.dc.html"


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
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


async def export_artboards(html_file: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    server = start_server(html_file.parent, PORT)
    url = f"http://localhost:{PORT}/{html_file.name}"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 3200, "height": 3200},
                device_scale_factor=1,
            )
            page = await context.new_page()

            print(f"Cargando: {url}")
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            await asyncio.sleep(10)  # bundler decompresses + renders

            # Artboards son los [data-dc-tpl] de 1080×1080 (o cuadrados ≥800px)
            cards = await page.evaluate("""
                () => {
                    const all = [...document.querySelectorAll('[data-dc-tpl]')];
                    return all
                        .filter(el => {
                            const r = el.getBoundingClientRect();
                            return r.width >= 800 && r.height >= 800
                                && Math.abs(r.width - r.height) < 50;
                        })
                        .map((el, i) => ({
                            tpl: el.getAttribute('data-dc-tpl'),
                            x: Math.round(el.getBoundingClientRect().left),
                            y: Math.round(el.getBoundingClientRect().top),
                            w: Math.round(el.getBoundingClientRect().width),
                            h: Math.round(el.getBoundingClientRect().height),
                        }));
                }
            """)
            print(f"Artboards 1:1 encontrados: {len(cards)}")

            saved = []
            for i, card in enumerate(cards, 1):
                fname    = f"rumbo_ola_{i:02d}.png"
                out_path = out_dir / fname
                print(f"  → post {i} ({card['w']}×{card['h']})")
                el = await page.query_selector(f"[data-dc-tpl='{card['tpl']}']")
                await el.screenshot(path=str(out_path))
                saved.append({"n": i, "tpl": card["tpl"], "file": str(out_path)})

            await browser.close()

    finally:
        server.shutdown()

    (out_dir / "_manifest.json").write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    print(f"\n✓ {len(saved)} PNGs guardados en {out_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Exporta posts de Rumbo OLA como PNGs")
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML, help="Archivo HTML descargado de Claude Design")
    parser.add_argument("--out",  type=Path, default=OUT_DIR,      help="Carpeta de salida")
    args = parser.parse_args()

    if not args.html.exists():
        print(f"ERROR: No encontré el archivo: {args.html}")
        print("Descargá el HTML de Claude Design y pasalo con --html /ruta/al/archivo.html")
        return

    asyncio.run(export_artboards(args.html, args.out))


if __name__ == "__main__":
    main()
