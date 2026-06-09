#!/usr/bin/env python3
"""
Parse a supplier price list (any format), add $70 USD markup, and generate posts.

Usage:
  # From a text file
  python tools/parse_supplier_list.py --file .tmp/supplier_list.txt

  # Paste directly in terminal (Ctrl+D to finish)
  python tools/parse_supplier_list.py

  # Dry run: show parsed items + markup without generating captions
  python tools/parse_supplier_list.py --file .tmp/supplier_list.txt --dry-run

  # Custom markup (default: 70)
  python tools/parse_supplier_list.py --file .tmp/supplier_list.txt --markup 80
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from tools.claude_call import call_claude
from tools.generate_tech_posts import generate_post, load_existing, save

load_dotenv()

TMP = ROOT / ".tmp"
OUTPUT = TMP / "tech_posts.json"


PARSE_PROMPT = """Tenés una lista de precios de un proveedor de tecnología. Extraé cada producto como un objeto JSON.

Para cada producto devolvé:
- "product": nombre completo del producto (marca + modelo + storage/RAM si aplica)
- "brand": "apple", "samsung", "playstation", u "other"
- "price_usd": precio en USD como número entero (sin símbolo, sin texto)

Si un item no tiene precio claro, igual incluilo con price_usd: null.
Ignorá encabezados, subtotales, saludos, o cualquier línea que no sea un producto.

Respondé SOLO con un array JSON válido, sin texto adicional.

Lista del proveedor:
{list}"""


def parse_list(raw: str) -> list[dict]:
    prompt = PARSE_PROMPT.format(list=raw.strip())
    result = call_claude(prompt, as_json=True)
    if isinstance(result, str):
        result = json.loads(result)
    return result


def main():
    parser = argparse.ArgumentParser(description="Parse supplier list and generate posts")
    parser.add_argument("--file", help="Path to supplier list .txt file")
    parser.add_argument("--markup", type=int, default=70, help="USD markup to add (default: 70)")
    parser.add_argument("--dry-run", action="store_true", help="Show parsed items without generating captions")
    parser.add_argument("--append", action="store_true", help="Append to existing tech_posts.json")
    args = parser.parse_args()

    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        print("Pegá la lista del proveedor (Ctrl+D cuando termines):")
        raw = sys.stdin.read()

    print("Parseando lista...")
    items = parse_list(raw)
    print(f"  {len(items)} productos encontrados\n")

    for item in items:
        price = item.get("price_usd")
        sale_price = (price + args.markup) if price is not None else None
        item["sale_price_usd"] = sale_price
        label = f"${sale_price}" if sale_price else "sin precio"
        print(f"  {item['brand'].upper():12} {item['product'][:45]:45} {label}")

    if args.dry_run:
        print("\n--dry-run: no se generaron captions.")
        return

    print("\nGenerando captions...")
    existing = load_existing() if args.append else []
    next_id = (max(p["id"] for p in existing) + 1) if existing else 1
    posts = list(existing)

    for i, item in enumerate(items):
        if item["sale_price_usd"] is None:
            print(f"  Saltando '{item['product']}' (sin precio)")
            continue
        print(f"  [{i+1}/{len(items)}] {item['product'][:50]}...")
        post = generate_post(
            brand=item["brand"] if item["brand"] in ("apple", "samsung", "playstation") else "apple",
            product=item["product"],
            price=str(item["sale_price_usd"]),
            post_type="offer",
            post_id=next_id + len(posts) - len(existing),
        )
        posts.append(post)

    TMP.mkdir(exist_ok=True)
    save(posts)
    new = len(posts) - len(existing)
    print(f"\nGuardado → {OUTPUT}  ({new} nuevo{'s' if new != 1 else ''}, {len(posts)} total)")
    print("Próximo paso: python tools/preview_tech_posts.py")


if __name__ == "__main__":
    main()
