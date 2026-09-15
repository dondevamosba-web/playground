#!/usr/bin/env python3
"""
Scrape product images from Pinterest and official brand pages for Techno posts.
Enriches the Techno calendar sheet with preview image URLs and generates
an HTML picker so you can choose the best image for each post.

Usage:
  python3 tools/scrape_product_images.py              # enrich all rows without Media URL
  python3 tools/scrape_product_images.py --preview    # also open HTML picker in browser
  python3 tools/scrape_product_images.py --dry-run    # show what would be scraped
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ENV_KEY   = "TECHNO_CONTENT_CALENDAR_SHEET_ID"
CACHE_PATH      = ROOT / ".tmp" / "techno_image_cache.json"
PREVIEW_HTML    = ROOT / ".tmp" / "techno_image_picker.html"
FIRECRAWL_KEY   = os.getenv("FIRECRAWL_API_KEY", "")

COL_DATE        = 0
COL_PRODUCT     = 3
COL_BRAND       = 4
COL_POST_TYPE   = 5
COL_MEDIA_URL   = 8
COL_STATUS      = 9
COL_PREVIEW_IMGS = 11   # column L — added by this script

# Product-specific page URLs — more precise than brand homepages
PRODUCT_PAGES = {
    "apple": {
        "iphone 17 pro max": "https://www.apple.com/iphone-17-pro/",
        "iphone 17 pro":     "https://www.apple.com/iphone-17-pro/",
        "iphone 17":         "https://www.apple.com/iphone-17/",
        "iphone air":        "https://www.apple.com/iphone-air/",
        "iphone 16 pro max": "https://www.apple.com/iphone-16-pro/",
        "iphone 16 pro":     "https://www.apple.com/iphone-16-pro/",
        "iphone 16":         "https://www.apple.com/iphone-16/",
        "macbook air m3":    "https://www.apple.com/macbook-air/",
        "macbook pro m4":    "https://www.apple.com/macbook-pro-14-and-16/",
        "airpods pro":       "https://www.apple.com/airpods-pro/",
        "airpods max":       "https://www.apple.com/airpods-max/",
        "ipad air":          "https://www.apple.com/ipad-air/",
        "apple watch series": "https://www.apple.com/apple-watch-series-10/",
        "apple watch ultra":  "https://www.apple.com/apple-watch-ultra/",
        "apple watch":        "https://www.apple.com/apple-watch-series-10/",
        "imac":               "https://www.apple.com/imac/",
        "mac mini":           "https://www.apple.com/mac-mini/",
    },
    "samsung": {
        "galaxy s25 ultra":  "https://www.samsung.com/us/smartphones/galaxy-s25-ultra/",
        "galaxy s25+":       "https://www.samsung.com/us/smartphones/galaxy-s25/",
        "galaxy s25":        "https://www.samsung.com/us/smartphones/galaxy-s25/",
        "galaxy tab s10":    "https://www.samsung.com/us/tablets/galaxy-tab-s10/",
        "galaxy buds3 pro":  "https://www.samsung.com/us/audio-sound/galaxy-buds/all-galaxy-buds/",
    },
    "playstation": {
        "ps5 slim":          "https://www.bhphotovideo.com/c/search?Ntt=ps5+slim",
        "ps5":               "https://www.bhphotovideo.com/c/search?Ntt=ps5+slim",
        "dualsense edge":    "https://www.playstation.com/en-us/accessories/dualsense-edge-wireless-controller/",
        "dualsense":         "https://www.bhphotovideo.com/c/search?Ntt=dualsense+controller",
    },
}

# Fallback: GSMArena for phones (no auth, good product images)
GSMARENA_SEARCH = "https://www.gsmarena.com/search.php3?sQuickSearch={query}"

# Hardcoded fallback press images for products that resist scraping.
# Refreshed 2026-07-18: the previous entries here were all dead links (2024
# Newsroom article paths that Apple has since retired, guessed Samsung/PS5
# gallery filenames that never existed) — 20 of 21 "found" candidates 404'd
# on direct fetch. Replaced with URLs verified live via curl -I at write time:
# Apple og:image meta tags (curl -L to follow redirects for retired models,
# which land on the current generation's page) and Samsung's server-rendered
# /buy/ page (samsung.com's own product pages are client-rendered JS with no
# og:image, but /buy/ ships real <img> tags in the raw HTML).
FALLBACK_IMAGES = {
    "playstation::ps5 slim":  [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6472/6472709_sd.jpg",
    ],
    "apple::iphone 17 pro": [
        "https://www.apple.com/v/iphone-17-pro/g/images/meta/iphone-17-pro_overview__eumhhclcpuaa_og.png",
    ],
    "apple::iphone 17": [
        "https://www.apple.com/v/iphone-17/g/images/meta/iphone-17_overview__cg0rlzmbhl7m_og.png",
    ],
    "apple::iphone air": [
        "https://www.apple.com/v/iphone-air/g/images/meta/iphone-air_overview__dwhg6l117yqa_og.png",
    ],
    "apple::iphone 16 pro": [
        "https://www.apple.com/v/iphone/home/cj/images/meta/iphone__bh930eyjnj0i_og.png",
    ],
    "apple::iphone 16": [
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-16-model-unselect-gallery-1-202409?wid=1200&hei=630&fmt=jpeg&qlt=95",
    ],
    # Split 13"/15" so both sizes don't show the identical stock photo —
    # user flagged this 2026-07-18 (3 MacBook Air cards all showing the
    # same image). Both from Apple's real M4 MacBook Air launch article.
    "apple::macbook air m4 13": [
        "https://www.apple.com/newsroom/images/2025/03/apple-introduces-the-new-macbook-air-with-the-m4-chip-and-a-sky-blue-color/article/Apple-MacBook-Air-Desk-View-250305_big.jpg.large.jpg",
    ],
    "apple::macbook air m4 15": [
        "https://www.apple.com/newsroom/images/2025/03/apple-introduces-the-new-macbook-air-with-the-m4-chip-and-a-sky-blue-color/article/Apple-MacBook-Air-hero-250305_big.jpg.large.jpg",
    ],
    "apple::macbook air": [
        "https://www.apple.com/v/macbook-air/z/images/meta/macbook_air_mx__ez5y0k5yy7au_og.png",
    ],
    "apple::macbook pro": [
        "https://www.apple.com/v/macbook-pro/ax/images/meta/macbook-pro__difvbgz1plsi_og.png",
    ],
    "apple::apple watch": [
        "https://www.apple.com/assets-www/en_WW/watch/og/watch_og_1ff2ee953.png",
    ],
    "apple::airpods pro": [
        "https://www.apple.com/v/airpods-pro/s/images/meta/og__c0ceegchesom_overview.png",
    ],
    "apple::airpods max": [
        "https://www.apple.com/v/airpods-max/k/images/meta/airpods-max_overview__c2mz40a3bugm_og.png",
    ],
    "apple::ipad air": [
        "https://www.apple.com/v/ipad-air/ah/images/meta/ipad-air_overview__bc2fd15uec0y_og.png",
    ],
    "apple::imac": [
        "https://www.apple.com/v/imac/v/images/meta/imac__d7trotporb6u_og.png",
    ],
    "apple::mac mini": [
        "https://www.apple.com/v/mac-mini/aa/images/meta/mac-mini__dvce2jrm11w2_og.jpg",
    ],
    "samsung::galaxy s25 ultra": [
        "https://images.samsung.com/is/image/samsung/p6pim/us/sm-s938uzbfxaa/gallery/us-galaxy-s25-s938-536276-sm-s938uzbfxaa-548617513",
    ],
    "samsung::galaxy s25+": [
        "https://images.samsung.com/is/image/samsung/p6pim/us/sm-s936udbaatt/gallery/us-galaxy-s25-s936-536278-sm-s936udbaatt-548474765",
    ],
    "samsung::galaxy s25": [
        "https://images.samsung.com/is/image/samsung/p6pim/us/sm-s936udbaatt/gallery/us-galaxy-s25-s936-536278-sm-s936udbaatt-548474765",
    ],
}

BRAND_COLORS = {
    "apple":       {"bg": "#1d1d1f", "accent": "#0071e3", "text": "#f5f5f7"},
    "samsung":     {"bg": "#1428a0", "accent": "#12d3ff", "text": "#ffffff"},
    "playstation": {"bg": "#003087", "accent": "#00aeef", "text": "#ffffff"},
}


# ── Firecrawl helpers ──────────────────────────────────────────────────────────

def firecrawl_scrape(url: str, wait_ms: int = 2000) -> dict:
    if not FIRECRAWL_KEY:
        print("  WARN: FIRECRAWL_API_KEY not set — skipping web scrape")
        return {}
    payload = json.dumps({
        "url": url,
        "formats": ["markdown", "html"],
        "actions": [{"type": "wait", "milliseconds": wait_ms}],
    }).encode()
    req = urllib.request.Request(
        "https://api.firecrawl.dev/v1/scrape",
        data=payload,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()).get("data", {})
    except Exception as e:
        print(f"  Firecrawl error: {e}")
        return {}


def extract_images(data: dict, brand: str) -> list[str]:
    """Pull image URLs from Firecrawl markdown/html response."""
    text = data.get("markdown", "") + data.get("html", "")

    patterns = [
        # Apple CDNs
        r'https://[^\s"\'<>]*(?:apple\.com|cdn-apple\.com|mzstatic\.com)[^\s"\'<>]*\.(?:jpg|jpeg|png|webp)',
        # Samsung CDNs
        r'https://[^\s"\'<>]*(?:samsung\.com|samsungmobilepress\.com)[^\s"\'<>]*\.(?:jpg|jpeg|png|webp)',
        # PlayStation CDNs
        r'https://[^\s"\'<>]*(?:playstation\.com|playstation\.net|gmedia\.playstation|image\.api\.playstation)[^\s"\'<>]*\.(?:jpg|jpeg|png|webp)',
        # GSMArena CDN
        r'https://fdn(?:2)?\.gsmarena\.com/[^\s"\'<>]+\.(?:jpg|jpeg|png)',
        # Generic large images (fallback)
        r'https://[^\s"\'<>]+(?:1200|1080|900|800|large|full|hero|product)[^\s"\'<>]*\.(?:jpg|jpeg|png|webp)',
    ]

    seen = set()
    urls = []
    skip = ("icon", "logo", "favicon", "avatar", "sprite", "badge", "thumbnail", "thumb", "tiny", "16x", "32x", "64x")
    for pat in patterns:
        for u in re.findall(pat, text, re.IGNORECASE):
            if u not in seen and not any(s in u.lower() for s in skip):
                seen.add(u)
                urls.append(u)

    return urls[:8]


# ── Image scraping per product ─────────────────────────────────────────────────

def _find_product_url(brand: str, product: str) -> str:
    product_lower = product.lower()
    pages = PRODUCT_PAGES.get(brand, {})
    # Try longest matching key first
    for key in sorted(pages, key=len, reverse=True):
        if key in product_lower:
            return pages[key]
    return ""


def scrape_official_page(brand: str, product: str) -> list[str]:
    url = _find_product_url(brand, product)
    if not url:
        return []
    print(f"  Official page: {url}")
    data = firecrawl_scrape(url, wait_ms=2000)
    return extract_images(data, brand)


def scrape_gsmarena(product: str) -> list[str]:
    query = urllib.parse.quote_plus(product.split()[0:3:1].__class__(product.split()[:3]).join(" ") if False else " ".join(product.split()[:3]))
    url = GSMARENA_SEARCH.format(query=urllib.parse.quote_plus(product))
    print(f"  GSMArena: {url[:80]}...")
    data = firecrawl_scrape(url, wait_ms=1000)
    imgs = re.findall(r'https://fdn2\.gsmarena\.com/[^\s"\'<>]+\.(?:jpg|jpeg|png)', data.get("html", ""), re.IGNORECASE)
    return list(dict.fromkeys(imgs))[:6]


def ddg_image_search(query: str) -> list[str]:
    """DuckDuckGo image search — no API key needed."""
    try:
        vqd_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}&iax=images&ia=images"
        req = urllib.request.Request(vqd_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        m = re.search(r'vqd=["\']([\d-]+)["\']', html)
        if not m:
            return []
        vqd = m.group(1)

        search_url = (
            "https://duckduckgo.com/i.js?"
            + urllib.parse.urlencode({"q": query, "o": "json", "vqd": vqd, "f": ",,,,,", "p": "1"})
        )
        req2 = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://duckduckgo.com/",
        })
        with urllib.request.urlopen(req2, timeout=10) as r2:
            data = json.loads(r2.read())

        results = data.get("results", [])
        urls = [r["image"] for r in results if r.get("image") and r.get("width", 0) >= 600]
        print(f"  DuckDuckGo: {len(urls)} images")
        return urls[:6]
    except Exception as e:
        print(f"  DuckDuckGo failed: {e}")
        return []


def get_images_for_product(brand: str, product: str, cache: dict) -> list[str]:
    key = f"{brand}::{product}"
    if key in cache and cache[key]:
        print(f"  Cache hit: {len(cache[key])} images")
        return cache[key]

    all_imgs = []
    all_imgs.extend(scrape_official_page(brand, product))
    time.sleep(0.8)
    # GSMArena fallback for phones
    if brand in ("apple", "samsung") and not all_imgs:
        all_imgs.extend(scrape_gsmarena(product))
        time.sleep(0.8)

    # Hardcoded fallback for products that resist scraping
    if not all_imgs:
        product_lower = product.lower()
        for fallback_key, fallback_imgs in FALLBACK_IMAGES.items():
            fb_brand, fb_product = fallback_key.split("::", 1)
            if fb_brand == brand and fb_product in product_lower:
                print(f"  Using press kit fallback: {len(fallback_imgs)} images")
                all_imgs.extend(fallback_imgs)
                break

    # DuckDuckGo image search as last resort
    if not all_imgs:
        query = f"{product} official product photo"
        all_imgs.extend(ddg_image_search(query))
        time.sleep(1.0)

    # Deduplicate preserving order
    seen = set()
    unique = [u for u in all_imgs if not (u in seen or seen.add(u))][:12]

    cache[key] = unique
    return unique


# ── Sheet operations ───────────────────────────────────────────────────────────

def ensure_preview_col_header(sheets, sheet_id):
    """Add 'Preview Images' header to column L if not already there."""
    existing = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="L1"
    ).execute().get("values", [[""]])
    if not existing or not existing[0]:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="L1",
            valueInputOption="RAW",
            body={"values": [["Preview Images"]]},
        ).execute()


def write_preview_images(sheets, sheet_id, row_idx, urls):
    range_str = f"L{row_idx + 2}"
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_str,
        valueInputOption="RAW",
        body={"values": [[", ".join(urls)]]},
    ).execute()


def update_media_url(sheets, sheet_id, row_idx, url):
    range_str = f"I{row_idx + 2}"
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_str,
        valueInputOption="RAW",
        body={"values": [[url]]},
    ).execute()
    print(f"    Sheet updated: Media URL → {url[:60]}")


# ── HTML picker ────────────────────────────────────────────────────────────────

def build_picker_html(posts_data: list) -> str:
    cards = "\n".join(_render_picker_card(p) for p in posts_data)

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Techno — Elegí imagen para cada post</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0a0a0a; color: #eee; }}

    .top-bar {{
      position: sticky; top: 0; background: #111; border-bottom: 1px solid #222;
      padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; z-index: 100;
    }}
    .top-bar h1 {{ font-size: 15px; font-weight: 600; color: #fff; }}
    .top-bar .meta {{ font-size: 13px; color: #666; }}
    .btn {{ background: #0095f6; color: white; border: none; border-radius: 8px;
            padding: 8px 18px; cursor: pointer; font-size: 13px; font-weight: 600; }}
    .btn:hover {{ background: #0081d6; }}

    .posts {{ display: flex; flex-direction: column; gap: 32px; padding: 28px 24px; max-width: 900px; margin: 0 auto; }}

    .post-block {{ background: #111; border-radius: 14px; border: 1px solid #222; overflow: hidden; }}
    .post-header {{ padding: 14px 18px; border-bottom: 1px solid #1e1e1e; display: flex; gap: 12px; align-items: center; }}
    .post-date {{ font-size: 12px; color: #888; }}
    .post-product {{ font-weight: 600; font-size: 14px; }}
    .brand-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}

    .caption-preview {{ padding: 14px 18px; font-size: 13px; color: #aaa; line-height: 1.55; border-bottom: 1px solid #1e1e1e; white-space: pre-wrap; }}

    .images-label {{ padding: 12px 18px 8px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: #555; font-weight: 600; }}
    .images-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; padding: 0 18px 18px; }}

    .img-option {{ position: relative; border-radius: 8px; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: border-color 0.15s; aspect-ratio: 1; }}
    .img-option:hover {{ border-color: #555; }}
    .img-option.selected {{ border-color: #0095f6; }}
    .img-option img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .img-option .tick {{ display: none; position: absolute; top: 6px; right: 6px; background: #0095f6;
                         border-radius: 50%; width: 22px; height: 22px; align-items: center; justify-content: center; font-size: 13px; }}
    .img-option.selected .tick {{ display: flex; }}

    .no-images {{ padding: 14px 18px; font-size: 13px; color: #555; font-style: italic; }}

    .commands-wrap {{ padding: 24px; max-width: 900px; margin: 0 auto; }}
    .commands-box {{ background: #0d0d0d; border: 1px solid #222; color: #a8ff78; padding: 20px; border-radius: 10px; font-family: monospace; font-size: 13px; white-space: pre-wrap; line-height: 1.6; display: none; }}
    .commands-box.visible {{ display: block; }}
  </style>
</head>
<body>

<div class="top-bar">
  <div>
    <h1>@techno.apple.ok — Elegí imagen para cada post</h1>
    <div class="meta" id="summary">Seleccioná una imagen por post</div>
  </div>
  <button class="btn" onclick="generateCommands()">Generar comandos de actualización</button>
</div>

<div class="posts">
  {cards}
</div>

<div class="commands-wrap">
  <div id="commands-box" class="commands-box"></div>
</div>

<script>
const selections = {{}};

function selectImage(postIdx, rowIdx, url) {{
  // Deselect all in this post
  document.querySelectorAll(`[data-post="${{postIdx}}"]`).forEach(el => el.classList.remove("selected"));
  // Select clicked
  const el = document.querySelector(`[data-post="${{postIdx}}"][data-url="${{CSS.escape(url)}}"]`);
  if (el) el.classList.add("selected");
  selections[postIdx] = {{ rowIdx, url }};
  updateSummary();
}}

function updateSummary() {{
  const count = Object.keys(selections).length;
  document.getElementById("summary").textContent = `${{count}} imagen${{count !== 1 ? "es" : ""}} seleccionada${{count !== 1 ? "s" : ""}}`;
}}

function generateCommands() {{
  if (!Object.keys(selections).length) {{
    alert("Seleccioná al menos una imagen primero.");
    return;
  }}
  const lines = [];
  Object.entries(selections).forEach(([postIdx, {{ rowIdx, url }}]) => {{
    lines.push(`python3 tools/scrape_product_images.py --set-url ${{rowIdx}} "${{url}}"`);
  }});
  const box = document.getElementById("commands-box");
  box.textContent = lines.join("\\n");
  box.classList.add("visible");
  box.scrollIntoView({{ behavior: "smooth" }});
}}
</script>
</body>
</html>'''


def _render_picker_card(p: dict) -> str:
    brand = p["brand"]
    colors = BRAND_COLORS.get(brand, BRAND_COLORS["apple"])
    images = p.get("preview_images", [])
    post_idx = p["post_idx"]
    row_idx = p["row_idx"]

    badge = f'<span class="brand-badge" style="background:{colors["bg"]};color:{colors["text"]};">{brand}</span>'

    if images:
        img_items = "\n".join(
            f'''<div class="img-option" data-post="{post_idx}" data-url="{url}"
                     onclick="selectImage({post_idx}, {row_idx}, '{url}')">
                 <img src="{url}" loading="lazy" onerror="this.parentElement.style.display='none'">
                 <div class="tick">✓</div>
               </div>'''
            for url in images
        )
        images_section = f'<div class="images-label">Elegí una imagen ({len(images)} opciones)</div><div class="images-grid">{img_items}</div>'
    else:
        images_section = '<div class="no-images">No se encontraron imágenes — subí una manualmente en el sheet.</div>'

    caption_preview = (p.get("caption", "")[:200] + "...").replace("<", "&lt;").replace(">", "&gt;")

    return f'''
    <div class="post-block">
      <div class="post-header">
        {badge}
        <div>
          <div class="post-product">{p.get("product", brand)}</div>
          <div class="post-date">{p.get("date", "")} {p.get("time", "")} · {p.get("post_type", "")}</div>
        </div>
      </div>
      <div class="caption-preview">{caption_preview}</div>
      {images_section}
    </div>'''


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--preview",  action="store_true", help="Open HTML picker in browser after scraping")
    parser.add_argument("--set-url",  type=int, metavar="ROW_IDX", help="Set Media URL for a specific row (used by picker commands)")
    parser.add_argument("url",        nargs="?", help="URL to set (used with --set-url)")
    args = parser.parse_args()

    sheet_id = os.getenv(SHEET_ENV_KEY)
    if not sheet_id:
        print(f"ERROR: {SHEET_ENV_KEY} not set. Run fill_content_techno.py first.")
        sys.exit(1)

    sheets, _ = get_services()

    # Handle --set-url (called from picker-generated commands)
    if args.set_url is not None:
        if not args.url:
            print("Usage: --set-url ROW_IDX <url>")
            sys.exit(1)
        update_media_url(sheets, sheet_id, args.set_url, args.url)
        return

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:L1000"
    ).execute().get("values", [])

    # Load image cache
    CACHE_PATH.parent.mkdir(exist_ok=True)
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}

    # Only process rows without a Media URL
    to_enrich = [
        (i, row) for i, row in enumerate(rows)
        if len(row) > COL_PRODUCT and (len(row) <= COL_MEDIA_URL or not row[COL_MEDIA_URL].strip())
    ]

    if not to_enrich:
        print("All rows already have Media URLs. Nothing to enrich.")
    else:
        print(f"{len(to_enrich)} posts without images — scraping now...\n")

    posts_data = []
    for i, (row_idx, row) in enumerate(to_enrich):
        product   = row[COL_PRODUCT] if len(row) > COL_PRODUCT else ""
        brand     = row[COL_BRAND]   if len(row) > COL_BRAND   else "apple"
        post_type = row[COL_POST_TYPE] if len(row) > COL_POST_TYPE else "offer"
        caption   = row[6] if len(row) > 6 else ""
        date_str  = row[COL_DATE] if len(row) > COL_DATE else ""
        time_str  = row[1] if len(row) > 1 else ""

        print(f"[{i+1}/{len(to_enrich)}] {brand.upper()} — {product or '(meme)'}")

        if args.dry_run:
            imgs = ["(would scrape)"]
        else:
            imgs = get_images_for_product(brand, product or brand, cache)
            print(f"  {len(imgs)} images found")

            if not args.dry_run and imgs:
                ensure_preview_col_header(sheets, sheet_id)
                write_preview_images(sheets, sheet_id, row_idx, imgs)

        posts_data.append({
            "post_idx":      i,
            "row_idx":       row_idx,
            "brand":         brand,
            "product":       product,
            "post_type":     post_type,
            "caption":       caption,
            "date":          date_str,
            "time":          time_str,
            "preview_images": imgs,
        })

        time.sleep(0.5)

    # Save updated cache
    if not args.dry_run:
        CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
        print(f"\nCache saved → {CACHE_PATH}")

    # Generate HTML picker
    html = build_picker_html(posts_data)
    PREVIEW_HTML.parent.mkdir(exist_ok=True)
    PREVIEW_HTML.write_text(html, encoding="utf-8")
    print(f"Picker HTML → {PREVIEW_HTML}")

    if args.preview or not args.dry_run:
        if sys.platform == "darwin":
            subprocess.run(["open", str(PREVIEW_HTML)])
        else:
            import webbrowser
            webbrowser.open(str(PREVIEW_HTML))

    print("\nNext: pick an image in the browser, then run the generated commands to update the sheet.")


if __name__ == "__main__":
    main()
