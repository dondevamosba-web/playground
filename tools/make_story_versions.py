#!/usr/bin/env python3
"""
Generate 1080x1920 story versions from 1080x1080 feed PNGs.
The feed square is centered on a brand-colored vertical canvas.

Usage:
  python tools/make_story_versions.py --dir .tmp/storm_posts --bg "#0c0817"
  python tools/make_story_versions.py --dir .tmp/ola_digital_posts --bg "#0F172A"
  python tools/make_story_versions.py --dir .tmp/storm_posts --bg "#0c0817" --skip-existing
"""

import argparse
from pathlib import Path
from PIL import Image


STORY_W = 1080
STORY_H = 1920


def make_story(feed_path: Path, bg_hex: str) -> Path:
    story_path = feed_path.parent / (feed_path.stem + "_story" + feed_path.suffix)
    feed = Image.open(feed_path).convert("RGBA")

    # Normalize to exactly 1080 wide (in case screenshots differ by 1px)
    if feed.width != STORY_W:
        ratio = STORY_W / feed.width
        feed = feed.resize((STORY_W, round(feed.height * ratio)), Image.LANCZOS)

    # Parse hex color
    bg_hex = bg_hex.lstrip("#")
    bg_color = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    canvas = Image.new("RGBA", (STORY_W, STORY_H), bg_color)

    # Center the feed image vertically (slightly above center looks more natural)
    y_offset = (STORY_H - feed.height) // 2
    canvas.paste(feed, (0, y_offset), feed)

    canvas.convert("RGB").save(str(story_path), "PNG", optimize=True)
    return story_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, type=Path)
    parser.add_argument("--bg", default="#0c0817", help="Background hex color e.g. #0c0817")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if _story.png already exists")
    args = parser.parse_args()

    source_dir = Path(args.dir)
    if not source_dir.exists():
        print(f"ERROR: directory not found: {source_dir}")
        return

    pngs = sorted(p for p in source_dir.glob("*.png") if not p.stem.endswith("_story"))
    print(f"Found {len(pngs)} feed PNGs in {source_dir}")

    generated = 0
    for feed_path in pngs:
        story_path = feed_path.parent / (feed_path.stem + "_story" + feed_path.suffix)
        if args.skip_existing and story_path.exists():
            continue
        out = make_story(feed_path, args.bg)
        print(f"  ✓ {out.name}")
        generated += 1

    print(f"\nDone. {generated} story versions generated.")


if __name__ == "__main__":
    main()
