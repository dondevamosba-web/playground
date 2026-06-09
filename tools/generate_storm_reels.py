#!/usr/bin/env python3
"""
Storm Digital — Reel Generator
One reel: "Your Google Ads Are Bleeding Money" (CPL proof)
1080×1920 · 30fps · ~20s · no camera footage required.

Usage:
  python3 tools/generate_storm_reels.py
  python3 tools/generate_storm_reels.py --output /custom/dir
"""

import argparse
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, concatenate_videoclips

W, H  = 1080, 1920
FPS   = 30
ROOT  = Path(__file__).parent.parent
OUT   = ROOT / ".tmp" / "storm_reels"

# ── Brand palette ─────────────────────────────────────────────────────────────
CORAL  = (170, 45,  0)
FOREST = (10,  46,  14)
DARK   = (24,  29,  38)
CREAM  = (245, 233, 212)
WHITE  = (255, 255, 255)
MUTED  = (65,  69,  77)
STORM_BLUE = (17, 71, 232)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
IDX_BLACK = 9   # Condensed Black — headlines
IDX_BOLD  = 1   # Bold            — subheads
IDX_REG   = 0   # Regular         — small labels

_cache = {}

def F(size, weight="black"):
    idx = {"black": IDX_BLACK, "bold": IDX_BOLD, "reg": IDX_REG}[weight]
    k = (size, idx)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONT_PATH, size, index=idx)
    return _cache[k]


# ── Easing ────────────────────────────────────────────────────────────────────
def expo_out(t, dur):
    p = min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0
    return 1 - (1 - p) ** 4

def smooth(t, dur):
    p = min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0
    return p * p * (3 - 2 * p)

def fade(t, dur):
    return min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0


# ── Drawing helpers ───────────────────────────────────────────────────────────
def centered_x(draw, text, font, w=W):
    bb = draw.textbbox((0, 0), text, font=font)
    return (w - (bb[2] - bb[0])) // 2

def text_w(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def text_h(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def draw_wordmark(draw, x, y, surface="dark", size=28):
    """Storm Digital wordmark with lightning bolt."""
    bolt_color = STORM_BLUE if surface in ("dark", "coral", "forest") else CORAL
    text_color = WHITE if surface in ("dark", "coral", "forest") else DARK
    muted_color = tuple(int(c * 0.55) for c in WHITE) if surface in ("dark", "coral", "forest") else MUTED

    # Lightning bolt — simple polygon
    bw = int(size * 0.75)
    bh = int(size * 1.1)
    pts = [
        (x + bw,     y),
        (x + bw // 2, y + bh // 2),
        (x + bw,     y + bh // 2),
        (x,          y + bh),
        (x + bw // 2, y + bh // 2 + 2),
        (x,          y + bh // 2 + 2),
    ]
    draw.polygon(pts, fill=bolt_color)

    tx = x + bw + 10
    draw.text((tx, y - 2), "STORM", font=F(size, "black"), fill=text_color)
    sw = text_w(draw, "STORM", F(size, "black"))
    draw.text((tx + sw + 8, y - 2), "DIGITAL", font=F(size, "reg"), fill=muted_color)


def draw_url(draw, surface="dark"):
    """storm.mkt.agency bottom-right."""
    color = tuple(int(c * 0.45) for c in WHITE) if surface in ("dark", "coral", "forest") else MUTED
    url = "storm.mkt.agency"
    f = F(22, "reg")
    uw = text_w(draw, url, f)
    draw.text((W - 64 - uw, H - 64), url, font=f, fill=color)


# ── Scene builders ─────────────────────────────────────────────────────────────
#
# Scene 1  (0–4s):  CORAL bg · eyebrow · "$120" as current "average"
# Scene 2  (4–9s):  DARK bg  · "$120" strikethrough → "$38" slams in
# Scene 3  (9–14s): DARK bg  · 3-line explanation (targeting, landing page, bids)
# Scene 4 (14–20s): FOREST bg · CTA — "storm.mkt.agency · Free Audit"
#

def scene_1(t):
    """Coral opener: industry average CPL reveal."""
    dur = 4.0
    img = Image.new("RGB", (W, H), CORAL)
    draw = ImageDraw.Draw(img)

    draw_wordmark(draw, 64, 72, surface="coral")
    draw_url(draw, surface="coral")

    # Eyebrow
    ey_p = fade(t, 0.5)
    ey_y = int(300 - (1 - ey_p) * 30)
    ey_color = (*WHITE, int(255 * ey_p * 0.72))
    draw.text((64, ey_y), "COST PER LEAD", font=F(26, "bold"),
              fill=tuple(int(c * 0.72) for c in WHITE))

    # "INDUSTRY" label
    il_p = fade(max(0, t - 0.3), 0.5)
    draw.text((64, 360), "INDUSTRY AVERAGE", font=F(32, "bold"),
              fill=tuple(int(c * il_p) for c in WHITE))

    # Big $120 number
    num_p = expo_out(max(0, t - 0.6), 0.7)
    num_y = int(480 + (1 - num_p) * 80)
    draw.text((centered_x(draw, "$120", F(220, "black")), num_y),
              "$120", font=F(220, "black"), fill=WHITE)

    # "per lead" sub-label
    sub_p = fade(max(0, t - 1.2), 0.5)
    draw.text((centered_x(draw, "per lead", F(44, "reg")), 760),
              "per lead", font=F(44, "reg"),
              fill=tuple(int(c * sub_p * 0.7) for c in WHITE))

    # Swipe hint at bottom
    swipe_p = fade(max(0, t - 2.5), 0.6)
    draw.text((centered_x(draw, "We do better →", F(28, "reg")), H - 160),
              "We do better →", font=F(28, "reg"),
              fill=tuple(int(c * swipe_p * 0.6) for c in WHITE))

    return np.array(img)


def scene_2(t):
    """Dark bg: $120 crossed out, $38 slams in."""
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    draw_wordmark(draw, 64, 72, surface="dark")
    draw_url(draw, surface="dark")

    # "Our roofing clients" label
    lbl_p = fade(t, 0.4)
    draw.text((64, 300), "OUR ROOFING CLIENTS", font=F(26, "bold"),
              fill=tuple(int(c * lbl_p * 0.7) for c in WHITE))

    # $120 with strikethrough
    old_p = min(1.0, t / 0.3)
    strike_p = smooth(max(0, t - 0.5), 0.5)  # 0→1 strikethrough progress
    old_color = tuple(int(c * old_p * 0.45) for c in WHITE)
    old_x = centered_x(draw, "$120", F(130, "black"))
    old_y = 370
    draw.text((old_x, old_y), "$120", font=F(130, "black"), fill=old_color)
    # strikethrough line
    if strike_p > 0:
        sw = text_w(draw, "$120", F(130, "black"))
        sy = old_y + 65
        line_end_x = int(old_x + sw * strike_p)
        strike_color = tuple(int(c * 0.6) for c in (220, 60, 40))
        draw.line([(old_x - 4, sy), (line_end_x, sy)], fill=strike_color, width=8)

    # $38 — appears after brief delay, zooms in
    new_p = expo_out(max(0, t - 1.0), 0.6)
    if new_p > 0:
        scale = 0.4 + new_p * 0.6
        num_str = "$38"
        big_font_size = int(220 * scale)
        big_font_size = max(40, big_font_size)
        f_big = F(big_font_size, "black")
        nx = centered_x(draw, num_str, f_big)
        ny = int(560 - (1 - new_p) * 60)
        # coral glow behind number
        glow_r = int(180 * new_p)
        glow_color = tuple(int(c * new_p * 0.35) for c in CORAL)
        draw.ellipse([(W//2 - glow_r, ny + 40 - glow_r//2),
                      (W//2 + glow_r, ny + 40 + glow_r//2)],
                     fill=glow_color)
        alpha_color = tuple(int(c * new_p) for c in CORAL)
        draw.text((nx, ny), num_str, font=f_big, fill=alpha_color)

    # "per lead  ·  after 90 days" sub-label
    sub_p = fade(max(0, t - 1.7), 0.5)
    sub = "per lead  ·  after 90 days"
    draw.text((centered_x(draw, sub, F(32, "reg")), 800),
              sub, font=F(32, "reg"),
              fill=tuple(int(c * sub_p * 0.65) for c in WHITE))

    return np.array(img)


def scene_3(t):
    """Dark bg: 3 reasons for the gap."""
    img = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(img)

    draw_wordmark(draw, 64, 72, surface="dark")
    draw_url(draw, surface="dark")

    # Headline
    h_p = expo_out(t, 0.5)
    hy = int(280 - (1 - h_p) * 40)
    draw.text((64, hy), "THE GAP COMES FROM:", font=F(36, "bold"),
              fill=tuple(int(c * h_p * 0.7) for c in WHITE))

    items = [
        ("01", "Smarter keyword targeting"),
        ("02", "Service-specific landing pages"),
        ("03", "Weekly bid management"),
    ]
    for i, (num, text) in enumerate(items):
        delay = 0.6 + i * 0.5
        ip = expo_out(max(0, t - delay), 0.45)
        iy = int(420 + i * 180 - (1 - ip) * 50)
        alpha = ip

        # Number
        draw.text((64, iy), num, font=F(48, "black"),
                  fill=tuple(int(c * alpha) for c in CORAL))
        # Divider
        div_x = 64 + text_w(draw, num, F(48, "black")) + 20
        draw.line([(div_x, iy + 12), (div_x, iy + 52)],
                  fill=tuple(int(c * alpha * 0.35) for c in WHITE), width=2)
        # Text
        draw.text((div_x + 24, iy + 4), text, font=F(44, "bold"),
                  fill=tuple(int(c * alpha) for c in WHITE))

    # Closing line
    close_p = fade(max(0, t - 2.4), 0.6)
    close = "We fix all three. Week one."
    draw.text((centered_x(draw, close, F(34, "reg")), 980),
              close, font=F(34, "reg"),
              fill=tuple(int(c * close_p * 0.6) for c in WHITE))

    return np.array(img)


def scene_4(t):
    """Forest bg: CTA."""
    img = Image.new("RGB", (W, H), FOREST)
    draw = ImageDraw.Draw(img)

    draw_wordmark(draw, 64, 72, surface="forest")
    draw_url(draw, surface="forest")

    # Top label
    lbl_p = fade(t, 0.4)
    draw.text((64, 300), "FREE AUDIT", font=F(26, "bold"),
              fill=tuple(int(c * lbl_p * 0.65) for c in WHITE))

    # Main headline
    h1_p = expo_out(max(0, t - 0.3), 0.55)
    h1_y = int(380 - (1 - h1_p) * 50)
    draw.text((64, h1_y), "15 minutes.", font=F(110, "black"),
              fill=tuple(int(c * h1_p) for c in WHITE))

    h2_p = expo_out(max(0, t - 0.65), 0.55)
    h2_y = int(500 - (1 - h2_p) * 50)
    draw.text((64, h2_y), "No pitch.", font=F(110, "black"),
              fill=tuple(int(c * h2_p) for c in WHITE))

    h3_p = expo_out(max(0, t - 1.0), 0.55)
    h3_y = int(620 - (1 - h3_p) * 50)
    draw.text((64, h3_y), "No contracts.", font=F(110, "black"),
              fill=tuple(int(c * h3_p) for c in WHITE))

    # Sub lede
    sub_p = fade(max(0, t - 1.6), 0.6)
    sub = "We show you where your leads are leaking.\nYou decide if we can help."
    line1, line2 = sub.split("\n")
    sub_y = 790
    for line in [line1, line2]:
        draw.text((64, sub_y), line, font=F(32, "reg"),
                  fill=tuple(int(c * sub_p * 0.72) for c in WHITE))
        sub_y += 52

    # URL pill / CTA
    cta_p = expo_out(max(0, t - 2.2), 0.6)
    cta_text = "storm.mkt.agency"
    cta_font = F(44, "bold")
    cw = text_w(draw, cta_text, cta_font)
    ch = 80
    cx = 64
    cy = 930
    pad_x, pad_y = 32, 16
    # pill background
    coral_alpha = tuple(int(c * cta_p) for c in CORAL)
    draw.rounded_rectangle(
        [(cx, cy), (cx + cw + pad_x * 2, cy + ch)],
        radius=40,
        fill=coral_alpha,
    )
    draw.text((cx + pad_x, cy + pad_y - 4), cta_text, font=cta_font,
              fill=tuple(int(c * cta_p) for c in WHITE))

    # DM tagline
    dm_p = fade(max(0, t - 3.0), 0.5)
    dm = "DM us \"AUDIT\" to get started"
    draw.text((centered_x(draw, dm, F(30, "reg")), 1040),
              dm, font=F(30, "reg"),
              fill=tuple(int(c * dm_p * 0.55) for c in WHITE))

    return np.array(img)


# ── Assemble ──────────────────────────────────────────────────────────────────

SCENES = [
    (scene_1, 4.0),
    (scene_2, 5.0),
    (scene_3, 5.0),
    (scene_4, 6.0),
]


def make_clip(fn, duration):
    def frame(t):
        return fn(t)
    return VideoClip(frame, duration=duration).with_fps(FPS)


def build_reel(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "reel_1_cpl_proof.mp4"

    print("Building Storm Digital reel: CPL Proof ($120 → $38)")
    clips = [make_clip(fn, dur) for fn, dur in SCENES]
    reel = concatenate_videoclips(clips, method="compose")
    reel.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        logger=None,
    )
    print(f"\n✓ Reel saved → {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate Storm Digital reel")
    parser.add_argument("--output", type=Path, default=OUT, help="Output directory")
    args = parser.parse_args()
    build_reel(args.output)


if __name__ == "__main__":
    main()
