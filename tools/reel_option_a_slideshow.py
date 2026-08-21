#!/usr/bin/env python3
"""
Option A — Slideshow Reel
Claude-generated script + Pillow brand slides + gTTS voiceover + FFmpeg → Instagram Reel

Usage:
  python3 tools/reel_option_a_slideshow.py --topic "5 errores en Instagram" --output .tmp/reels/option_a.mp4
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from gtts import gTTS
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp" / "reels"
TMP.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "tools"))
from claude_call import call_claude

BRAND = {
    "bg":     (12,  74, 110),   # #0C4A6E
    "dark":   (7,   30,  46),   # #071E2E
    "accent": (14, 165, 233),   # #0EA5E9
    "cyan":   (6,  182, 212),   # #06B6D4
    "teal":   (56, 189, 248),   # #38BDF8
    "orange": (249,115,  22),   # #F97316
    "white":  (255,255,255),
    "gray":   (148,163,184),
}

REEL_W, REEL_H = 1080, 1920
SLIDE_DURATION = 3.5
FPS = 30


def generate_script(topic: str) -> list[dict]:
    prompt = f"""Sos estratega de contenido para Ola Digital, agencia digital de Olavarría, Buenos Aires, Argentina.
Generá un reel de Instagram de 5 slides sobre: {topic}

Tono: profesional, directo, bonaerense. Usá 'vos'.

Respondé SOLO JSON válido, sin markdown, sin comentarios:
{{"slides": [
  {{"headline": "máx 5 palabras en mayúsculas", "subtext": "1 línea de apoyo", "voiceover": "15-20 palabras en español rioplatense", "bg_variant": "dark|mid|light"}},
  ...
]}}
bg_variant: dark=#071E2E, mid=#0C4A6E, light=#0EA5E9"""

    # haiku: structured JSON output following explicit format, mechanical
    raw = call_claude(prompt, model="haiku")
    # Strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    data = json.loads(cleaned.strip())
    return data["slides"]


def gradient_rect(draw, x0, y0, x1, y1, color_top, color_bottom):
    for y in range(y0, y1):
        t = (y - y0) / max(y1 - y0, 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        draw.line([(x0, y), (x1, y)], fill=(r, g, b))


def draw_wave(draw, y_base, width, height, color, opacity=80):
    """Draw decorative wave shape."""
    import math
    points = []
    steps = 200
    for i in range(steps + 1):
        x = int(i * width / steps)
        y = y_base + int(math.sin(i * 2 * math.pi / steps * 3) * height)
        points.append((x, y))
    points += [(width, REEL_H), (0, REEL_H)]
    overlay = Image.new("RGBA", (width, REEL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.polygon(points, fill=(*color, opacity))
    return overlay


def make_slide_image(slide: dict, index: int) -> Path:
    out_path = TMP / f"slide_a_{index}.png"

    bg_variants = {
        "dark":  (BRAND["dark"],  BRAND["bg"]),
        "mid":   (BRAND["bg"],    (10, 55, 90)),
        "light": ((8, 100, 150),  BRAND["bg"]),
    }
    top_color, bot_color = bg_variants.get(slide.get("bg_variant", "mid"), bg_variants["mid"])

    img = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    gradient_rect(draw, 0, 0, REEL_W, REEL_H, top_color, bot_color)

    # Decorative wave overlay
    wave = draw_wave(draw, int(REEL_H * 0.55), REEL_W, 80, BRAND["accent"], opacity=25)
    img = Image.alpha_composite(img, wave)
    draw = ImageDraw.Draw(img)

    # Big background number (watermark style)
    try:
        num_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 500)
    except Exception:
        num_font = ImageFont.load_default()
    draw.text((REEL_W // 2, REEL_H // 2), str(index + 1),
              font=num_font, fill=(*BRAND["accent"], 18), anchor="mm")

    # Top logo bar
    try:
        logo_font  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        body_font  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 52)
        head_font  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 92)
    except Exception:
        logo_font = small_font = body_font = head_font = ImageFont.load_default()

    # Logo pill
    draw.rounded_rectangle([64, 64, 200, 128], radius=16,
                            fill=(*BRAND["accent"], 255))
    draw.text((132, 96), "O", font=logo_font, fill=BRAND["white"], anchor="mm")
    draw.text((218, 96), "OLA", font=logo_font, fill=BRAND["white"], anchor="lm")
    draw.text((304, 96), "Digital", font=small_font, fill=BRAND["cyan"], anchor="lm")

    # Slide counter top-right
    draw.text((REEL_W - 72, 96), f"{index + 1}/5",
              font=small_font, fill=BRAND["orange"], anchor="rm")

    # Horizontal rule
    draw.line([(64, 148), (REEL_W - 64, 148)], fill=(*BRAND["accent"], 40), width=1)

    # Bottom content block
    text_y = REEL_H - 440

    # Eyebrow accent line
    draw.rounded_rectangle([64, text_y - 8, 200, text_y + 8], radius=4,
                            fill=(*BRAND["orange"], 255))

    text_y += 36

    # Headline — wrap manually
    headline = slide["headline"].upper()
    max_width = REEL_W - 128
    # Simple word wrap
    words = headline.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=head_font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        draw.text((64, text_y), line, font=head_font, fill=BRAND["white"])
        bbox = draw.textbbox((64, text_y), line, font=head_font)
        text_y += bbox[3] - bbox[1] + 12

    text_y += 20

    # Subtext
    draw.text((64, text_y), slide["subtext"], font=body_font, fill=BRAND["cyan"])

    # Bottom gradient fade
    fade = Image.new("RGBA", (REEL_W, 200), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(200):
        alpha = int(180 * y / 200)
        fd.line([(0, y), (REEL_W, y)], fill=(7, 30, 46, alpha))
    img.paste(fade, (0, REEL_H - 200), fade)

    final = img.convert("RGB")
    final.save(out_path)
    return out_path


def make_voiceover(slides: list[dict]) -> Path:
    text = ". ".join(s["voiceover"] for s in slides)
    tts = gTTS(text=text, lang="es", tld="com.ar", slow=False)
    path = TMP / "voiceover_a.mp3"
    tts.save(str(path))
    return path


def build_reel(slides: list[dict], output: Path) -> Path:
    print("Generating slide images...")
    img_paths = [make_slide_image(s, i) for i, s in enumerate(slides)]

    print("Generating voiceover...")
    audio_path = make_voiceover(slides)

    print("Building video...")
    clips = []
    for img_path in img_paths:
        clips.append(ImageClip(str(img_path)).with_duration(SLIDE_DURATION))

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(str(audio_path))
    if audio.duration > video.duration:
        audio = audio.subclipped(0, video.duration)
    video = video.with_audio(audio)

    output.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(output), fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=str(TMP / "tmp_audio_a.m4a"), logger=None,
    )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="Los 5 errores que cometen los negocios en Instagram en Olavarría")
    parser.add_argument("--output", default=str(ROOT / ".tmp" / "reels" / "option_a.mp4"))
    args = parser.parse_args()

    print(f"Generating script: {args.topic}")
    slides = generate_script(args.topic)
    print(f"Got {len(slides)} slides:")
    for i, s in enumerate(slides):
        print(f"  {i+1}. {s['headline']}")

    build_reel(slides, Path(args.output))
    print(f"\nOption A saved: {args.output}")


if __name__ == "__main__":
    main()
