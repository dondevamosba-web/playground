#!/usr/bin/env python3
"""
Turn brand-toolkit/storm-posts/*.html into LinkedIn carousel PDFs (1080×1080 pages).

Usage:
  python3 tools/storm_linkedin_carousel.py --list                 # show themes
  python3 tools/storm_linkedin_carousel.py                        # build all default themes
  python3 tools/storm_linkedin_carousel.py --theme results
  python3 tools/storm_linkedin_carousel.py --posts "01,09,10" --name custom
Output: .tmp/linkedin_carousels/<theme>.pdf
"""
import argparse
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
POSTS = ROOT / "brand-toolkit" / "storm-posts"
OUT = ROOT / ".tmp" / "linkedin_carousels"

# Slides referenced by leading file number; order matters.
THEMES = {
    "results": ["01", "06", "23", "24", "44", "35", "09"],
    "playbook": ["38", "25", "36", "33", "43", "48", "34"],
    "trust": ["02", "03", "42", "46", "29", "26", "09"],
    "waste": ["39", "30", "10", "21", "27", "34"],
}


def find(num):
    matches = list(POSTS.glob(f"{num} *.html"))
    if not matches:
        sys.exit(f"No post file starting with '{num}' in {POSTS}")
    return matches[0]


def shoot(files, page):
    imgs = []
    for f in files:
        page.set_viewport_size({"width": 1080, "height": 1080})
        page.goto(f.as_uri())
        page.wait_for_timeout(400)
        png = OUT / f"_{f.stem}.png"
        page.screenshot(path=str(png))
        imgs.append(Image.open(png).convert("RGB"))
    return imgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=sorted(THEMES))
    ap.add_argument("--posts", help="Comma-separated post numbers, e.g. 01,09,10")
    ap.add_argument("--name", default="custom")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list:
        for t, nums in THEMES.items():
            print(f"{t}: {', '.join(find(n).stem for n in nums)}")
        return

    if a.posts:
        jobs = {a.name: [n.strip() for n in a.posts.split(",")]}
    elif a.theme:
        jobs = {a.theme: THEMES[a.theme]}
    else:
        jobs = THEMES

    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for name, nums in jobs.items():
            imgs = shoot([find(n) for n in nums], page)
            pdf = OUT / f"storm_{name}.pdf"
            imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=96)
            print(f"Wrote {pdf} ({len(imgs)} slides)")
        browser.close()
    for tmp in OUT.glob("_*.png"):
        tmp.unlink()


if __name__ == "__main__":
    main()
