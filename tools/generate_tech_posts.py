#!/usr/bin/env python3
"""
Generate product posts for @techno.apple.ok (Apple, Samsung, PlayStation).

Usage:
  python tools/generate_tech_posts.py --brand apple --product "iPhone 16 Pro Max 256GB" --price "1.500.000" --type offer
  python tools/generate_tech_posts.py --brand samsung --product "Galaxy S25 Ultra" --price "1.200.000" --type feature --count 3
  python tools/generate_tech_posts.py --brand playstation --product "PS5 Slim" --type launch --price "850.000"
  python tools/generate_tech_posts.py --brand apple --type meme --count 2
  python tools/generate_tech_posts.py --append --brand samsung --product "Galaxy A55" --price "600.000" --type offer
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from tools.claude_call import call_claude

load_dotenv()

OUTPUT = ROOT / ".tmp" / "tech_posts.json"

WHATSAPP = os.getenv("TECHNO_WHATSAPP", "")

BRAND_HASHTAGS = {
    "apple": ["#apple", "#iphone", "#ios", "#applefan", "#manzanita"],
    "samsung": ["#samsung", "#galaxy", "#android", "#samsungfan", "#teamsamsung"],
    "playstation": ["#playstation", "#ps5", "#gaming", "#gamer", "#sonyplaystation"],
}

GENERAL_HASHTAGS = ["#tecnologia", "#tech", "#argentina", "#technoargentina", "#gadgets", "#tiendatech"]

SYSTEM_PROMPT = """Sos el community manager de @techno.apple.ok, una tienda de tecnología en Argentina que vende Apple, Samsung y PlayStation.

Tu voz: directa, joven, rioplatense. Hablás de vos (no de usted). Sin corporativismos. Nada de "¡No te lo pierdas!" ni frases genéricas.

Reglas estrictas:
- Nunca empieces con ¿ (sin signo de apertura de interrogación)
- Sin emojis al principio de las oraciones
- Precios en USD: formato $650, $1.200, etc.
- Máximo 5 hashtags, todos en minúsculas

Formatos por tipo de post:
- offer: precio prominente + 1 diferenciador clave + CTA al WhatsApp ("{whatsapp}")
- feature: nombre del producto + 3 características con emoji + CTA suave
- launch: "Llegó" o "Ya disponible" + qué lo hace especial + CTA
- meme: humor relatable sobre la marca/producto, sin precio, solo engagement

Respondé SOLO con JSON válido, sin texto adicional:
{{"caption": "...", "hashtags": ["#tag1", "#tag2", "#tag3"]}}"""


def build_prompt(brand: str, product: str, price: str, post_type: str) -> str:
    parts = [f"Tipo de post: {post_type}", f"Marca: {brand.capitalize()}"]
    if product:
        parts.append(f"Producto: {product}")
    if price:
        parts.append(f"Precio: ${price}")
    return "\n".join(parts)


def generate_post(brand: str, product: str, price: str, post_type: str, post_id: int) -> dict:
    whatsapp_link = f"https://wa.me/{WHATSAPP.lstrip('+').replace(' ', '')}" if WHATSAPP else "WhatsApp (configurar TECHNO_WHATSAPP en .env)"
    system = SYSTEM_PROMPT.format(whatsapp=whatsapp_link)
    prompt = build_prompt(brand, product, price, post_type)

    schema = {
        "type": "object",
        "properties": {
            "caption": {"type": "string"},
            "hashtags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["caption", "hashtags"],
    }
    result = call_claude(prompt, system_prompt=system, schema=schema)

    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {"caption": result, "hashtags": []}

    brand_tags = BRAND_HASHTAGS.get(brand, [])
    extra_tags = GENERAL_HASHTAGS[:3]
    all_hashtags = result.get("hashtags", []) + [t for t in brand_tags + extra_tags if t not in result.get("hashtags", [])]

    return {
        "id": post_id,
        "brand": brand,
        "product": product or "",
        "price": price or "",
        "type": post_type,
        "caption": result.get("caption", ""),
        "hashtags": all_hashtags[:10],
        "image_url": None,
        "approved": None,
    }


def load_existing() -> list:
    if OUTPUT.exists():
        with open(OUTPUT, encoding="utf-8") as f:
            return json.load(f)
    return []


def save(posts: list):
    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate posts for @techno.apple.ok")
    parser.add_argument("--brand", required=True, choices=["apple", "samsung", "playstation"])
    parser.add_argument("--product", default="", help="Product name and variant")
    parser.add_argument("--price", default="", help="Price in USD (e.g. 650)")
    parser.add_argument("--type", dest="post_type", default="offer",
                        choices=["offer", "feature", "launch", "meme"])
    parser.add_argument("--count", type=int, default=1, help="Number of post variations to generate")
    parser.add_argument("--append", action="store_true", help="Append to existing .tmp/tech_posts.json instead of replacing")
    args = parser.parse_args()

    existing = load_existing() if args.append else []
    next_id = (max(p["id"] for p in existing) + 1) if existing else 1

    posts = list(existing)
    for i in range(args.count):
        print(f"Generating post {i + 1}/{args.count} ({args.post_type}, {args.brand})...")
        post = generate_post(args.brand, args.product, args.price, args.post_type, next_id + i)
        posts.append(post)
        print(f"  ID {post['id']}: {post['caption'][:60]}...")

    save(posts)
    total = len(posts)
    new = args.count
    print(f"\nGuardado → {OUTPUT}  ({new} nuevo{'s' if new > 1 else ''}, {total} total)")
    print("Próximo paso: python tools/preview_tech_posts.py")


if __name__ == "__main__":
    main()
