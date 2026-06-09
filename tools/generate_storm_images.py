#!/usr/bin/env python3
"""
Generate Storm Digital Instagram post images with large, bold typography.
Exports 1080x1080px single images with brand colors.

Usage:
  python3 tools/generate_storm_images.py                    # generate all posts
  python3 tools/generate_storm_images.py --post 0           # generate post #0 only
  python3 tools/generate_storm_images.py --output /path/to  # custom output dir
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / ".tmp" / "storm_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand colors
COLORS = {
    "coral": "#aa2d00",
    "forest": "#0a2e0e",
    "cream": "#f5e9d4",
    "dark": "#181d26",
    "white": "#ffffff",
    "body": "#333840",
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
    return lines

def generate_post(post_data, output_path):
    """Generate a single Storm Digital post image."""
    w, h = 1080, 1080
    img = Image.new("RGB", (w, h), hex_to_rgb(COLORS[post_data["bg"]]))
    draw = ImageDraw.Draw(img)
    
    # Load fonts (fallback to default if not available)
    try:
        font_headline = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 76)  # Big headline
        font_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        font_eyebrow = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        font_url = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except:
        font_headline = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_eyebrow = ImageFont.load_default()
        font_url = ImageFont.load_default()
    
    # Determine text colors based on surface
    fg_color = hex_to_rgb(COLORS[post_data.get("fg", "white")])
    eyebrow_color_key = "coral" if post_data.get("fg") == "dark" else "white"
    eyebrow_color = hex_to_rgb(COLORS[eyebrow_color_key])
    
    # Padding
    pad = 64
    inner_w = w - (2 * pad)
    
    # Eyebrow (label)
    if "eyebrow" in post_data:
        draw.text((pad, pad + 40), post_data["eyebrow"], fill=eyebrow_color, font=font_eyebrow)
    
    # Headline (wrapped, LARGE)
    headline_y = pad + 120
    if "headline" in post_data:
        lines = wrap_text(post_data["headline"], font_headline, inner_w, draw)
        for i, line in enumerate(lines):
            draw.text((pad, headline_y + i * 100), line, fill=fg_color, font=font_headline)
        headline_y += len(lines) * 100 + 40
    
    # Body/lede
    if "lede" in post_data:
        lines = wrap_text(post_data["lede"], font_body, inner_w, draw)
        for i, line in enumerate(lines):
            draw.text((pad, headline_y + 60 + i * 50), line, fill=fg_color, font=font_body)
    
    # URL at bottom right
    draw.text((w - pad - 240, h - pad - 40), "storm.mkt.agency", fill=fg_color, font=font_url)
    
    # Date at bottom left
    draw.text((pad, h - pad - 40), post_data.get("date", ""), fill=fg_color, font=font_url)
    
    img.save(output_path)
    print(f"✓ Generated: {output_path.name}")

# Posts from calendar (headlines + CTAs)
POSTS = [
    {
        "date": "06/01",
        "bg": "coral",
        "fg": "white",
        "eyebrow": "BUILT FOR CONTRACTORS",
        "headline": "We generate leads for roofers, HVAC, windows, plumbers",
        "lede": "That's all we do. We're obsessed with your vertical.",
    },
    {
        "date": "06/03",
        "bg": "forest",
        "fg": "white",
        "eyebrow": "OUR FOCUS",
        "headline": "We only work with home service contractors.",
        "lede": "Deep vertical expertise means better results. We know your seasonality, your CPL benchmarks, your objections.",
    },
    {
        "date": "06/04",
        "bg": "dark",
        "fg": "white",
        "eyebrow": "FACT",
        "headline": "97% search online before calling.",
        "lede": "If you're not on page 1, you're invisible. We make sure you're there.",
    },
    {
        "date": "06/05",
        "bg": "coral",
        "fg": "white",
        "eyebrow": "PROOF",
        "headline": "Cost per lead: $38",
        "lede": "Our roofing clients beat industry average by 3.1x.",
    },
    {
        "date": "06/08",
        "bg": "cream",
        "fg": "dark",
        "eyebrow": "5 THINGS KILLING YOUR GOOGLE RANKING",
        "headline": "Missing GBP, zero reviews, slow mobile",
        "lede": "Fix these 5 and you'll see movement in 30 days.",
    },
    {
        "date": "06/10",
        "bg": "dark",
        "fg": "white",
        "eyebrow": "PAID ADS BLEEDING YOUR BUDGET?",
        "headline": "We audit your Google Ads for free.",
        "lede": "We'll find where you're wasting money and plug the leak.",
    },
    {
        "date": "06/12",
        "bg": "forest",
        "fg": "white",
        "eyebrow": "SOCIAL PROOF",
        "headline": "4.8-star average rating across our clients.",
        "lede": "When reviews are your job, you get good at asking.",
    },
]

def main():
    parser = argparse.ArgumentParser(description="Generate Storm Digital post images")
    parser.add_argument("--post", type=int, help="Generate specific post # (0-indexed)")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()
    
    args.output.mkdir(parents=True, exist_ok=True)
    
    if args.post is not None:
        if 0 <= args.post < len(POSTS):
            generate_post(POSTS[args.post], args.output / f"post_{args.post:02d}.png")
        else:
            print(f"ERROR: Post #{args.post} not found (0-{len(POSTS)-1})")
            sys.exit(1)
    else:
        for i, post in enumerate(POSTS):
            generate_post(post, args.output / f"post_{i:02d}.png")
    
    print(f"\n✓ All images saved to: {args.output}")

if __name__ == "__main__":
    main()
