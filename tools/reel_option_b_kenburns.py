#!/usr/bin/env python3
"""
Option B — Cinematic Ken Burns Reel
Claude script + Pillow cinematic slides + pan/zoom motion + gTTS → Instagram Reel

Usage:
  python3 tools/reel_option_b_kenburns.py --topic "Por qué tu web no trae clientes" --output .tmp/reels/option_b.mp4
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from gtts import gTTS
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoClip,
    TextClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFilter, ImageFont

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp" / "reels"
TMP.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "tools"))
from claude_call import call_claude

REEL_W, REEL_H = 1080, 1920
SLIDE_DURATION = 4.0
FPS = 30

PALETTES = [
    # bg_top, bg_bottom, accent, text
    ((5, 20, 40),   (10, 55, 90),  (6, 182, 212),   (255, 255, 255)),
    ((15, 10, 35),  (30, 20, 70),  (249, 115, 22),   (255, 255, 255)),
    ((3, 35, 55),   (6, 74, 110),  (56, 189, 248),   (255, 255, 255)),
    ((8, 40, 65),   (5, 20, 40),   (14, 165, 233),   (255, 255, 255)),
]

MOTIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right"]


def generate_script(topic: str) -> list[dict]:
    prompt = f"""Sos estratega de contenido para Ola Digital, agencia digital de Olavarría, Buenos Aires, Argentina.
Generá un reel cinematográfico de 4 escenas sobre: {topic}

Tono: impactante, profesional, bonaerense. Usá 'vos'. Cada escena tiene máximo impacto visual.

Respondé SOLO JSON válido, sin markdown:
{{"scenes": [
  {{"hook": "máx 4 palabras, mayúsculas, impacto máximo", "caption": "1 línea de apoyo contundente", "voiceover": "20-25 palabras rioplatense directo"}},
  ...
]}}"""

    raw = call_claude(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    data = json.loads(cleaned.strip())
    return data["scenes"]


def make_cinematic_frame(palette_idx: int, hook: str, caption: str) -> np.ndarray:
    """Render a single full-res cinematic slide."""
    # Oversized source for Ken Burns
    src_w = int(REEL_W * 1.35)
    src_h = int(REEL_H * 1.35)

    bg_top, bg_bot, accent, text_color = PALETTES[palette_idx % len(PALETTES)]

    img = Image.new("RGBA", (src_w, src_h))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(src_h):
        t = y / src_h
        r = int(bg_top[0] + (bg_bot[0] - bg_top[0]) * t)
        g = int(bg_top[1] + (bg_bot[1] - bg_top[1]) * t)
        b = int(bg_top[2] + (bg_bot[2] - bg_top[2]) * t)
        draw.line([(0, y), (src_w, y)], fill=(r, g, b, 255))

    # Abstract geometric — large circle
    cx, cy = int(src_w * 0.75), int(src_h * 0.3)
    r = int(src_w * 0.55)
    circle = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(circle)
    cd.ellipse([cx - r, cy - r, cx + r, cy + r],
               fill=(*accent, 20), outline=(*accent, 45), width=3)
    # Inner ring
    r2 = int(r * 0.65)
    cd.ellipse([cx - r2, cy - r2, cx + r2, cy + r2],
               outline=(*accent, 30), width=2)
    img = Image.alpha_composite(img, circle)
    draw = ImageDraw.Draw(img)

    # Diagonal lines (brand texture)
    for i in range(-src_h, src_w, 120):
        draw.line([(i, 0), (i + src_h, src_h)],
                  fill=(*accent, 12), width=1)

    # Bottom dark fade for text
    fade = Image.new("RGBA", (src_w, src_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    fade_start = int(src_h * 0.45)
    for y in range(fade_start, src_h):
        alpha = int(200 * (y - fade_start) / (src_h - fade_start))
        fd.line([(0, y), (src_w, y)], fill=(*bg_top, alpha))
    img = Image.alpha_composite(img, fade)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        hook_font    = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        caption_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 58)
        logo_font    = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        small_font   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except Exception:
        hook_font = caption_font = logo_font = small_font = ImageFont.load_default()

    # Logo top-left
    draw.rounded_rectangle([70, 70, 218, 138], radius=18, fill=(*accent, 230))
    draw.text((144, 104), "O", font=logo_font, fill=(255, 255, 255), anchor="mm")
    draw.text((236, 104), "OLA Digital", font=small_font, fill=(255, 255, 255), anchor="lm")

    # Hook — wrap
    hook_up = hook.upper()
    max_w = src_w - 140
    words = hook_up.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = draw.textbbox((0, 0), test, font=hook_font)
        if bb[2] - bb[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    text_y = src_h - 380 - len(lines) * 130
    for line in lines:
        draw.text((70, text_y), line, font=hook_font,
                  fill=text_color, stroke_width=2, stroke_fill=(0, 0, 0))
        bb = draw.textbbox((70, text_y), line, font=hook_font)
        text_y += (bb[3] - bb[1]) + 16

    text_y += 24

    # Accent bar
    draw.rounded_rectangle([70, text_y, 220, text_y + 8], radius=4, fill=(*accent, 255))
    text_y += 40

    # Caption
    draw.text((70, text_y), caption, font=caption_font, fill=accent)

    return np.array(img.convert("RGB"))


def apply_ken_burns(frame_np: np.ndarray, motion: str, duration: float, fps: int) -> ImageClip:
    src_h, src_w = frame_np.shape[:2]
    n_frames = int(duration * fps)
    frames = []

    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)

        if motion == "zoom_in":
            scale_t = 1.0 + 0.15 * t
            w = int(REEL_W / scale_t)
            h = int(REEL_H / scale_t)
            x0 = (src_w - w) // 2
            y0 = (src_h - h) // 2
        elif motion == "zoom_out":
            scale_t = 1.15 - 0.15 * t
            w = int(REEL_W / scale_t)
            h = int(REEL_H / scale_t)
            x0 = (src_w - w) // 2
            y0 = (src_h - h) // 2
        elif motion == "pan_left":
            w, h = REEL_W, REEL_H
            x0 = int((src_w - REEL_W) * t)
            y0 = (src_h - REEL_H) // 2
        else:  # pan_right
            w, h = REEL_W, REEL_H
            x0 = int((src_w - REEL_W) * (1 - t))
            y0 = (src_h - REEL_H) // 2

        x0 = max(0, min(x0, src_w - w))
        y0 = max(0, min(y0, src_h - h))

        crop = frame_np[y0:y0 + h, x0:x0 + w]
        resized = np.array(Image.fromarray(crop).resize((REEL_W, REEL_H), Image.LANCZOS))
        frames.append(resized)

    frames_np = np.stack(frames)

    def make_frame(t_sec):
        idx = min(int(t_sec * fps), len(frames_np) - 1)
        return frames_np[idx]

    return VideoClip(make_frame, duration=duration)


def make_voiceover(scenes: list[dict]) -> Path:
    text = ". ".join(s["voiceover"] for s in scenes)
    tts = gTTS(text=text, lang="es", tld="com.ar", slow=False)
    path = TMP / "voiceover_b.mp3"
    tts.save(str(path))
    return path


def build_reel(scenes: list[dict], output: Path) -> Path:
    clips = []
    for i, scene in enumerate(scenes):
        print(f"  Scene {i+1}: rendering frame...")
        frame = make_cinematic_frame(i, scene["hook"], scene["caption"])
        motion = MOTIONS[i % len(MOTIONS)]
        print(f"  Scene {i+1}: applying {motion}...")
        clip = apply_ken_burns(frame, motion, SLIDE_DURATION, FPS)
        clips.append(clip)

    print("Stitching...")
    video = concatenate_videoclips(clips, method="compose")

    print("Voiceover...")
    audio_path = make_voiceover(scenes)
    audio = AudioFileClip(str(audio_path))
    if audio.duration > video.duration:
        audio = audio.subclipped(0, video.duration)
    video = video.with_audio(audio)

    output.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(output), fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=str(TMP / "tmp_audio_b.m4a"), logger=None,
    )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="Por qué tu página web no te trae clientes nuevos")
    parser.add_argument("--output", default=str(ROOT / ".tmp" / "reels" / "option_b.mp4"))
    args = parser.parse_args()

    print(f"Script: {args.topic}")
    scenes = generate_script(args.topic)
    print(f"Got {len(scenes)} scenes:")
    for i, s in enumerate(scenes):
        print(f"  {i+1}. [{MOTIONS[i % len(MOTIONS)]}] {s['hook']}")

    print("\nBuilding reel...")
    build_reel(scenes, Path(args.output))
    print(f"\nOption B saved: {args.output}")


if __name__ == "__main__":
    main()
