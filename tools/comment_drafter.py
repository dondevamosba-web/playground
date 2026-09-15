#!/usr/bin/env python3
"""
Pull recent comments on our own IG posts (all 4 accounts) and draft replies
with Claude, respecting per-account voice rules. Nothing is posted — output
goes to .tmp/comment_replies.md for manual review.

Usage:
  python3 tools/comment_drafter.py                  # all accounts, last 5 posts each
  python3 tools/comment_drafter.py --account Fiestas --posts 10
  python3 tools/comment_drafter.py --no-claude      # just list comments, no drafts
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

GRAPH = "https://graph.facebook.com/v19.0"
TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
ACCOUNTS = {
    "Ola Digital": os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Storm": os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Fiestas": os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Techno": os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
}
VOICE = {
    "Ola Digital": "Castellano argentino, cercano y profesional. NUNCA abras con signo de pregunta invertido (¿).",
    "Storm": "English, punchy and confident, agency operator voice. Short.",
    "Fiestas": "Castellano argentino, tono fiestero pero útil. Si preguntan por entradas, derivar a link en bio.",
    "Techno": "Castellano argentino, vendedor confiable. Si preguntan precio, derivar a WhatsApp/DM. Nunca des precios de proveedor.",
}
SEEN_FILE = ROOT / ".tmp" / "replied_comment_ids.json"


def get(url, **params):
    params["access_token"] = TOKEN
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def draft_reply(account, post_caption, comment):
    from tools.claude_call import call_claude
    prompt = (f"Sos el community manager de la cuenta {account}. Voz: {VOICE[account]}\n"
              f"Post: {post_caption[:200]}\nComentario recibido: \"{comment}\"\n"
              "Escribí UNA respuesta breve (máx 2 líneas) lista para pegar. Solo la respuesta.")
    # sonnet: brand voice judgment, not mechanical formatting
    return call_claude(prompt, model="sonnet").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", choices=list(ACCOUNTS))
    ap.add_argument("--posts", type=int, default=5)
    ap.add_argument("--no-claude", action="store_true")
    a = ap.parse_args()

    seen = set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()
    accounts = {a.account: ACCOUNTS[a.account]} if a.account else ACCOUNTS
    lines = [f"# Respuestas a comentarios — {date.today()}\n"]
    new_ids, found = [], 0

    for name, ig_id in accounts.items():
        try:
            media = get(f"{GRAPH}/{ig_id}/media", fields="id,caption", limit=a.posts)["data"]
        except requests.RequestException as e:
            lines.append(f"\n## {name} — ERROR media: {e}\n")
            continue
        section = []
        for m in media:
            try:
                comments = get(f"{GRAPH}/{m['id']}/comments",
                               fields="id,text,username,timestamp")["data"]
            except requests.RequestException:
                continue
            for c in comments:
                if c["id"] in seen:
                    continue
                found += 1
                new_ids.append(c["id"])
                reply = "" if a.no_claude else draft_reply(name, m.get("caption", ""), c["text"])
                section.append(f"- **@{c['username']}**: {c['text']}\n  - ↳ borrador: {reply}")
        if section:
            lines.append(f"\n## {name}\n")
            lines.extend(section)

    out = ROOT / ".tmp" / "comment_replies.md"
    out.write_text("\n".join(lines))
    SEEN_FILE.write_text(json.dumps(sorted(seen | set(new_ids))))
    print(f"{found} comentarios nuevos → {out}")


if __name__ == "__main__":
    main()
