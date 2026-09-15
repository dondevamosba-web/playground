#!/usr/bin/env python3
"""Inyecta wishlist/wishlist.json en wishlist/index.html (placeholder /*WISHLIST_JSON*/{})."""
import json, re, pathlib

base = pathlib.Path(__file__).parent.parent / "wishlist"
data = json.loads((base / "wishlist.json").read_text())
html = (base / "index.html").read_text()
html = re.sub(r"/\*WISHLIST_JSON\*/[^\n]*;", "/*WISHLIST_JSON*/" + json.dumps(data, ensure_ascii=False) + ";", html)
(base / "index.html").write_text(html)
print(f"OK: {len(data['wishlist'])} ítems inyectados en wishlist/index.html")
