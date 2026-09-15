#!/usr/bin/env python3
"""
Compare prices for remodel materials using Easy.com.ar's public VTEX catalog API.
(MercadoLibre and Sodimac block scraping; Easy's API is open — see workflow notes.)

Usage:
  python3 tools/materiales_precios.py                          # default materials list
  python3 tools/materiales_precios.py --q "pintura latex 20l" --q "membrana liquida 20kg"
Output: prints table and writes olavarria/materiales_precios.md
"""
import argparse
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).parent.parent
API = "https://www.easy.com.ar/api/catalog_system/pub/products/search/"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

DEFAULT_QUERIES = [
    "porcelanato 60x60",
    "pintura latex interior 20l",
    "pintura latex exterior 20l",
    "membrana liquida 20kg",
    "griferia cocina monocomando",
    "griferia ducha",
    "inodoro con mochila",
    "luminaria spot embutido led",
    "pergola",
]


def search(q, top=3):
    # VTEX needs multi-word terms in the path with map=ft (query-param ft returns 400)
    r = requests.get(API + quote(q), params={"map": "ft", "_from": 0, "_to": 9},
                     headers=UA, timeout=20)
    r.raise_for_status()
    out = []
    for p in r.json():
        try:
            offer = p["items"][0]["sellers"][0]["commertialOffer"]
            if not offer.get("IsAvailable", True) or not offer.get("Price"):
                continue
            out.append({"name": p["productName"], "price": offer["Price"],
                        "url": f"https://www.easy.com.ar/{p['linkText']}/p"})
        except (KeyError, IndexError):
            continue
    return sorted(out, key=lambda x: x["price"])[:top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", action="append", help="Search query (repeatable)")
    a = ap.parse_args()
    queries = a.q or DEFAULT_QUERIES

    lines = [f"# Precios de materiales — Easy.com.ar\n\nActualizado: {date.today()}\n"]
    for q in queries:
        try:
            results = search(q)
        except requests.RequestException as e:
            print(f"{q}: ERROR {e}")
            continue
        print(f"\n{q}:")
        lines.append(f"\n## {q}\n")
        if not results:
            print("  (sin resultados)")
            lines.append("_Sin resultados._\n")
        for r in results:
            print(f"  ${r['price']:>12,.0f}  {r['name'][:60]}")
            lines.append(f"- ${r['price']:,.0f} — [{r['name']}]({r['url']})")

    out = ROOT / "olavarria" / "materiales_precios.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
