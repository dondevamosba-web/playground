"""
Resolver de fotos de producto para la landing de Techno.

Cuatro validaciones, no una:
  1. HTTP 200 y decodifica como imagen
  2. >= 600 px lado corto            -> mata los iconos de 47x84
  3. hash != placeholder de Best Buy -> mata el "Image Unavailable"
  4. slug de la URL contiene el modelo esperado -> mata el bug de familia
Ademas: hash unico entre productos distintos.
"""
import hashlib
import io
import os
import re

import requests
from PIL import Image

OUT = r"C:\Users\Guido\AppData\Local\Temp\claude\C--Users-Guido-OneDrive-Desktop-Personal\6e60b9e0-a4cf-4537-8fee-d7cc8de42179\scratchpad\prod"
os.makedirs(OUT, exist_ok=True)

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}

BB_PLACEHOLDER = "ef3719b2"  # prefijo md5 del "Image Unavailable" de Best Buy

# (etiqueta, url de la pagina, substring que DEBE estar en el slug de la imagen)
PRODUCTS = [
    ("AirPods Pro 3a Gen",   "https://www.apple.com/shop/buy-airpods/airpods-pro-3",   "airpods-pro-3"),
    ("Apple Watch S11 42MM", "https://www.apple.com/shop/buy-watch/apple-watch",       "watch"),
    ("iPad 11a Gen 128GB",   "https://www.apple.com/shop/buy-ipad/ipad",               "ipad"),
    ("iPhone 15 128GB",      "https://www.apple.com/shop/buy-iphone/iphone-15",        "iphone-15"),
    ("Mac mini M4 256GB",    "https://www.apple.com/shop/buy-mac/mac-mini",            "mac-mini"),
    ("iPhone 17 256GB",      "https://www.apple.com/shop/buy-iphone/iphone-17",        "iphone-17"),
    ("iPhone 17 Pro 256GB",  "https://www.apple.com/shop/buy-iphone/iphone-17-pro",    "iphone-17-pro"),
    ("MacBook Air M4 13in",  "https://www.apple.com/shop/buy-mac/macbook-air",         "macbook-air"),
]

IMG_PAT = re.compile(r'https://store\.storeimages\.cdn-apple\.com/[^\s"\'\\)]+')
SLUG_PAT = re.compile(r'/is/([a-z0-9\-]+)')


def candidates(html):
    """URLs de producto plausibles, mas grandes primero, sin banners ni logos."""
    seen, out = set(), []
    for u in IMG_PAT.findall(html):
        u = u.split("&amp;")[0]
        m = re.search(r"wid=(\d+)", u)
        wid = int(m.group(1)) if m else 0
        if wid < 600:
            continue
        slug = SLUG_PAT.search(u)
        slug = slug.group(1) if slug else ""
        if any(k in slug for k in ("banner", "logo", "applecard", "services-",
                                   "personal-setup", "trade-in", "financing")):
            continue
        if u in seen:
            continue
        seen.add(u)
        out.append((wid, slug, u))
    out.sort(key=lambda t: -t[0])
    return out


seen_hashes = {}
results = []

for label, page, must in PRODUCTS:
    row = {"label": label, "status": None, "slug": None, "url": None, "dim": None}
    try:
        r = requests.get(page, headers=H, timeout=30)
        if r.status_code != 200:
            row["status"] = f"pagina HTTP {r.status_code}"
            results.append(row); continue
        cands = candidates(r.text)
        matching = [c for c in cands if must in c[1]]
        if not matching:
            slugs = sorted({c[1][:44] for c in cands})[:5]
            row["status"] = f"ningun slug con '{must}'"
            row["slug"] = " | ".join(slugs)
            results.append(row); continue

        picked = False
        for wid, slug, url in matching[:6]:
            try:
                ir = requests.get(url, headers=H, timeout=30)
                if ir.status_code != 200:
                    continue
                b = ir.content
                h = hashlib.md5(b).hexdigest()
                if h.startswith(BB_PLACEHOLDER):
                    continue
                im = Image.open(io.BytesIO(b)); im.load()
                if min(im.width, im.height) < 600:
                    continue
                if h in seen_hashes and seen_hashes[h] != label:
                    row["status"] = f"DUPLICADA de {seen_hashes[h]}"
                    continue
                seen_hashes[h] = label
                fn = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") + ".png"
                if im.mode in ("RGBA", "P", "LA"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    rgba = im.convert("RGBA")
                    bg.paste(rgba, mask=rgba.split()[-1]); im = bg
                im.convert("RGB").save(os.path.join(OUT, fn))
                row.update(status="OK", slug=slug, url=url,
                           dim=f"{im.width}x{im.height} {len(b)//1024}KB", file=fn)
                picked = True
                break
            except Exception:
                continue
        if not picked and row["status"] is None:
            row["status"] = "ninguna candidata paso validacion"
    except Exception as e:
        row["status"] = f"{type(e).__name__}: {e}"
    results.append(row)

print(f"{'PRODUCTO':<24} {'ESTADO':<26} {'DIMENSIONES':<18} SLUG")
print("-" * 110)
for r in results:
    print(f"{r['label']:<24} {str(r['status']):<26} {str(r.get('dim') or ''):<18} {str(r.get('slug') or '')[:44]}")

ok = [r for r in results if r["status"] == "OK"]
print(f"\nresueltas: {len(ok)}/{len(PRODUCTS)}   hashes distintos: {len(seen_hashes)}")
print(f"guardadas en: {OUT}")
