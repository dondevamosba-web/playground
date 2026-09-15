#!/usr/bin/env python3
"""
Convert a square feed-post image into a 1080×1920 story:
blurred fill background, centered post, account handle on top.

Usage:
  python3 tools/post_to_story.py .tmp/posts/foo.png --handle @storm.digital
  python3 tools/post_to_story.py .tmp/posts/*.png --handle @techno.apple.ok --out-dir .tmp/stories
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920


def make_story(src: Path, handle: str, out_dir: Path) -> Path:
    post = Image.open(src).convert("RGB")
    # background: post scaled to fill 1080×1920, heavily blurred and darkened
    bg = post.resize((W, int(W * post.height / post.width)))
    if bg.height < H:
        bg = bg.resize((int(H * bg.width / bg.height), H))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
                  (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.55))

    post = post.resize((960, int(960 * post.height / post.width)))
    bg.paste(post, ((W - post.width) // 2, (H - post.height) // 2))

    d = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
    d.text((W // 2, 130), handle, font=font, fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, H - 140), "nuevo post — link en bio", font=font, fill=(230, 230, 230), anchor="mm")

    out = out_dir / f"{src.stem}_story.png"
    bg.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--handle", required=True)
    ap.add_argument("--out-dir", default=".tmp/stories")
    a = ap.parse_args()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for img in a.images:
        print("Wrote", make_story(Path(img), a.handle, out_dir))


if __name__ == "__main__":
    main()
