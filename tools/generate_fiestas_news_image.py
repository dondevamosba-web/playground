#!/usr/bin/env python3
"""
Generate a Fiestas-branded news image for Miss Monique BIORHYTHM.
Uses the original artist photo as background, new layout + no infoticketsarg branding.
Output: .tmp/fiestas_miss_monique.jpg (1080x1080)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests, io

ROOT = Path(__file__).parent.parent
OUT = ROOT / ".tmp" / "fiestas_miss_monique.jpg"
FONT_DIN_BOLD = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
FONT_ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"

W, H = 1080, 1080

# --- Download artist photo (same photo, different crop/treatment) ---
PHOTO_URL = "https://instagram.fmdq6-1.fna.fbcdn.net/v/t51.82787-15/708102478_18082197455398812_3706749675840480054_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=109&ig_cache_key=MzkwNzIxOTczNzc0NDQ0MTc2MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=kUtuvVg5UfwQ7kNvwE5xXty&_nc_oc=AdqMCmEugziUts66lYZ3wfr6cdFVNj7_4xjPxL-y2ZCnnrTQ8mIhsfS5ktbanv5rdfs&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=instagram.fmdq6-1.fna&_nc_gid=fCNsQHyBIGevQpxbY_0WGQ&_nc_ss=7a3ba&oh=00_Af9RVNsyhFtwrZckDXsLIZMnA_1WATGyW-XUt-X-sK58JA&oe=6A2CB589"

r = requests.get(PHOTO_URL, timeout=15)
photo = Image.open(io.BytesIO(r.content)).convert("RGB")

# Crop to 1080x1080 from center-top (show her face + upper body)
orig_w, orig_h = photo.size
# Original is 1080x1350 — crop top 1080px
crop_box = (0, 0, orig_w, orig_w)  # square from top
photo = photo.crop(crop_box).resize((W, H), Image.LANCZOS)

# Slightly desaturate and cool the tones for a different mood
from PIL import ImageEnhance
photo = ImageEnhance.Color(photo).enhance(0.75)  # desaturate slightly
photo = ImageEnhance.Contrast(photo).enhance(1.1)

canvas = Image.new("RGB", (W, H))
canvas.paste(photo)

draw = ImageDraw.Draw(canvas)

# --- Dark overlays ---
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)

# Heavy gradient: starts at 25%, full black by 60%
for y in range(H):
    start = int(H * 0.25)
    if y < start:
        alpha = 0
    else:
        alpha = int(255 * min(1.0, (y - start) / (H * 0.38)))
    od.rectangle([(0, y), (W, y + 1)], fill=(0, 0, 0, alpha))

# Cover entire top strip AFTER gradient to wipe original "INFO." text
od.rectangle([(0, 0), (W, 230)], fill=(0, 0, 0, 255))

canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
draw = ImageDraw.Draw(canvas)

# --- Accent color: electric teal/cyan line ---
TEAL = (0, 230, 200)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)

# Thin horizontal accent line
line_y = int(H * 0.58)
draw.rectangle([(60, line_y), (W - 60, line_y + 3)], fill=TEAL)

# --- "NOTICIAS" pill top-left ---
try:
    font_tag = ImageFont.truetype(FONT_DIN_BOLD, 28)
except:
    font_tag = ImageFont.load_default()

tag_text = "NOTICIAS"
tag_bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
tag_w = tag_bbox[2] - tag_bbox[0]
pad = 14
draw.rectangle([(52, 60), (52 + tag_w + pad*2, 60 + 36)], fill=TEAL)
draw.text((52 + pad, 62), tag_text, font=font_tag, fill=(0, 0, 0))

# --- Main headline ---
try:
    font_big = ImageFont.truetype(FONT_DIN_BOLD, 100)
    font_mid = ImageFont.truetype(FONT_DIN_BOLD, 68)
    font_small = ImageFont.truetype(FONT_ARIAL_BOLD, 34)
    font_detail = ImageFont.truetype(FONT_ARIAL_BOLD, 28)
except:
    font_big = font_mid = font_small = font_detail = ImageFont.load_default()

# Line 1: "MISS MONIQUE"
y = line_y + 18
draw.text((60, y), "MISS MONIQUE", font=font_big, fill=WHITE)

# Line 2: "PRESENTA BIORHYTHM"
y += 105
draw.text((60, y), "PRESENTA", font=font_mid, fill=WHITE)
draw.text((60 + draw.textlength("PRESENTA ", font=font_mid), y), "BIORHYTHM", font=font_mid, fill=TEAL)

# Line 3: date + venue
y += 80
draw.text((60, y), "SÁB 03 DE OCTUBRE  ·  23:00 HS", font=font_small, fill=GRAY)

# Line 4: venue
y += 46
draw.text((60, y), "MANDARINE PARK, PUNTA CARRASCO — BUENOS AIRES", font=font_detail, fill=GRAY)

# --- Save ---
OUT.parent.mkdir(exist_ok=True)
canvas.save(OUT, "JPEG", quality=95)
print(f"Saved: {OUT}")
print(f"Size: {canvas.size}")
