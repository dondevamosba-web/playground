#!/usr/bin/env python3
"""Baja un thumbnail por ítem de la wishlist (DuckDuckGo Images) a wishlist/img/<id>.jpg
y guarda el campo "imagen" en wishlist.json. Salta ítems que ya tienen imagen local."""
import json, pathlib, re, subprocess, time, urllib.parse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
base = pathlib.Path(__file__).parent.parent / "wishlist"
imgdir = base / "img"
imgdir.mkdir(exist_ok=True)
data = json.loads((base / "wishlist.json").read_text())

def curl(url):
    return subprocess.run(["curl", "-s", "--compressed", "-A", UA, url],
                          capture_output=True, timeout=30).stdout

def ddg_thumb(query):
    q = urllib.parse.quote_plus(query)
    html = curl(f"https://duckduckgo.com/?q={q}&iax=images&ia=images").decode(errors="ignore")
    m = re.search(r'vqd=\\?"([0-9-]+)\\?"', html)
    if not m:
        return None
    res = curl(f"https://duckduckgo.com/i.js?l=us-en&o=json&q={q}&vqd={m.group(1)}&p=1")
    try:
        results = json.loads(res)["results"]
    except Exception:
        return None
    return results[0]["thumbnail"] if results else None

for item in data["wishlist"]:
    dest = imgdir / f"{item['id']}.jpg"
    if item.get("imagen") and dest.exists():
        continue
    query = item["nombre"]
    thumb = ddg_thumb(query + " product")
    if not thumb:
        print(f"  ✗ {item['nombre']}: sin resultado")
        continue
    img = curl(thumb)
    if len(img) < 1000:
        print(f"  ✗ {item['nombre']}: descarga falló")
        continue
    dest.write_bytes(img)
    item["imagen"] = f"img/{item['id']}.jpg"
    print(f"  ✓ {item['nombre']} -> {dest.name} ({len(img)//1024} KB)")
    time.sleep(1)

(base / "wishlist.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print("wishlist.json actualizado")
