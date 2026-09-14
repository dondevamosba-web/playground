#!/usr/bin/env python3
"""Fiestas branded announcement card (1080x1080). Cachea por hash de evento."""
import argparse, io, re, sys
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from tools.render_cache import cached_render

W, H = 1080, 1080
ACCENT = (183, 106, 255)
ACCENT_DEEP = (46, 16, 78)
WHITE = (255, 255, 255)
BLACK = (10, 6, 16)
HANDLE = "@fiestaselectronicasbuenosaires"
FONT_DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MESES = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]


def f(path, size):
    for candidate in (path, "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _background(photo_bytes):
    if photo_bytes:
        try:
            ph = Image.open(io.BytesIO(photo_bytes)).convert("RGB")
            ow, oh = ph.size
            scale = max(W / ow, H / oh)
            ph = ph.resize((int(ow * scale) + 1, int(oh * scale) + 1), Image.LANCZOS)
            nw, nh = ph.size
            ph = ph.crop(((nw - W) // 2, (nh - H) // 3, (nw - W) // 2 + W, (nh - H) // 3 + H))
            ph = ImageEnhance.Brightness(ph).enhance(0.62)
            ph = ImageEnhance.Color(ph).enhance(0.55)
            return ph
        except Exception:
            pass
    bg = Image.new("RGB", (W, H), BLACK)
    glow = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(glow)
    d.ellipse([W//2-420, H//2-420, W//2+420, H//2+420], fill=ACCENT_DEEP)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    return Image.blend(bg, glow, 0.9)


def make_card(event: dict, photo_bytes: bytes | None = None) -> Path:
    name = (event.get("name") or "").strip()
    venue = (event.get("venue") or "").split(",")[0].strip()
    lineup = (event.get("lineup") or "").strip()
    ev_date = (event.get("date") or "").strip()

    safe = re.sub(r"[^\w]", "_", name)[:40] or "card"
    out = ROOT / ".tmp" / f"fiestas_card_{safe}_{ev_date}.jpg"

    def render():
        img = _background(photo_bytes)
        grad = Image.new("L", (1, H), 0)
        for y in range(H):
            grad.putpixel((0, y), min(235, max(0, int((y - H*0.42) / (H*0.58) * 235))))
        img.paste(Image.new("RGB", (W, H), BLACK), (0, 0), grad.resize((W, H)))
        d = ImageDraw.Draw(img)

        chip_txt = "FIESTAS ELECTRÓNICAS"
        cf = f(FONT_DIN, 44)
        tw = d.textlength(chip_txt, font=cf)
        d.rectangle([48, 52, 48+tw+44, 118], fill=ACCENT)
        d.text((48+22, 108), chip_txt, font=cf, fill=BLACK, anchor="lb")

        title = name.upper()
        words = title.split()
        max_width = W - 120
        size = 128
        while True:
            big = f(FONT_DIN, size)
            lines, cur = [], ""
            for w_ in words:
                t = (cur + " " + w_).strip()
                if d.textlength(t, font=big) > max_width and cur:
                    lines.append(cur); cur = w_
                else:
                    cur = t
            lines.append(cur)
            if len(lines) <= 2 or size <= 60:
                break
            size -= 8

        tag = "EVENTO RECOMENDADO"
        tf = f(FONT_ARIAL, 30)
        ty = H - 360 - (len(lines)-1) * 118
        tw = d.textlength(tag, font=tf)
        d.rectangle([56, ty, 56+tw+36, ty+54], fill=ACCENT)
        d.text((56+18, ty+27), tag, font=tf, fill=BLACK, anchor="lm")

        y = ty + 92
        for ln in lines:
            d.text((56, y), ln, font=big, fill=WHITE)
            y += 118

        try:
            dt = datetime.strptime(ev_date, "%Y-%m-%d")
            date_str = f"{dt.day:02d} {MESES[dt.month-1]}"
        except Exception:
            date_str = ev_date
        info = " · ".join(x for x in (date_str, venue, lineup.split(",")[0].strip()) if x)
        d.text((56, y+14), info, font=f(FONT_DIN, 60), fill=ACCENT)

        hf = f(FONT_ARIAL, 26)
        d.text((W-40, H-36), HANDLE, font=hf, fill=(255,255,255,160), anchor="rb")
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, quality=92)

    # nota: si hay foto (photo_bytes), no cacheamos por bytes de la foto (sería
    # una key gigante) — cacheamos por (name, date, venue) nomás. Si cambia la
    # foto pero no esos 3 campos, no se re-renderiza; ok para este caso de uso
    # porque el flujo normal es un evento -> una foto fija.
    cached_render("flyer_card", [name, ev_date, venue], out, render_fn=render)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--date", default="")
    ap.add_argument("--venue", default="")
    ap.add_argument("--lineup", default="")
    ap.add_argument("--photo", default="")
    a = ap.parse_args()
    photo = None
    if a.photo:
        r = requests.get(a.photo, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        photo = r.content
    p = make_card({"name": a.name, "date": a.date, "venue": a.venue, "lineup": a.lineup}, photo)
    print(p)
