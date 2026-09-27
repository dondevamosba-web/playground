#!/usr/bin/env python3
"""
Link enricher — gets a title for every saved link (bare ones first), groups them by topic
and feeds the titles into the notes RAG search index.

  YouTube / X / TikTok → official public oEmbed endpoints (no key)
  Anything else        → og:title / og:description / <title> of the page
  Instagram often blocks anonymous reads: those stay as "sin título" and are grouped by domain.

Results are cached in the RAG DB (table links): each URL is fetched once.

Usage:
  python3 tools/enrich_links.py              # enrich new links, write .tmp/notes_rag/links.md
  python3 tools/enrich_links.py --all        # include links that already have a note
  python3 tools/enrich_links.py --limit 50
"""
import argparse
import html
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import notes_rag as rag

OUT = rag.DATA / "links.md"
UA = {"User-Agent": "Mozilla/5.0 (compatible; facebookexternalhit/1.1)"}

OEMBED = {
    "youtube.com": "https://www.youtube.com/oembed?format=json&url={}",
    "youtu.be":    "https://www.youtube.com/oembed?format=json&url={}",
    "x.com":       "https://publish.twitter.com/oembed?omit_script=1&url={}",
    "twitter.com": "https://publish.twitter.com/oembed?omit_script=1&url={}",
    "tiktok.com":  "https://www.tiktok.com/oembed?url={}",
}

TOPICS = {
    "🤖 IA y código": ["claude", "gpt", "ai ", " ia ", "agent", "agente", "prompt", "mcp", "code", "código", "github",
                      "repo", "cursor", "automat", "n8n", "llm", "vibe"],
    "📣 Marketing y ads": ["ads", "marketing", "meta", "ugc", "seo", "funnel", "leads", "ventas", "brand", "marca",
                          "anuncio", "copy", "creativ"],
    "🎨 Diseño y web": ["design", "diseño", "web", "landing", "ui", "ux", "figma", "framer", "logo", "font"],
    "🏠 Casa y deco": ["casa", "cocina", "deco", "interior", "mueble", "arquitect", "baño", "living", "reforma"],
    "💪 Salud y fitness": ["gym", "fitness", "entren", "workout", "dieta", "salud", "protein", "running", "ski"],
    "🧠 Psicología": ["psicolog", "pareja", "terapia", "ansiedad", "vínculo", "relación", "duelo", "apego"],
}


def _domain(url):
    return re.sub(r"^https?://(www\.|m\.|vt\.)?([^/]+).*", r"\2", url)


def _strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def fetch_title(url, get=requests.get):
    """Return a short human title for url, or '' if the site does not tell."""
    dom = _domain(url)
    api = next((tpl for d, tpl in OEMBED.items() if dom.endswith(d)), None)
    try:
        if api:
            data = get(api.format(quote(url, safe="")), headers=UA, timeout=15).json()
            text = data.get("title") or _strip_tags(data.get("html", ""))
            author = data.get("author_name", "")
            return f"{author}: {text}"[:200] if author and text else (text or author)[:200]
        page = get(url, headers=UA, timeout=15).text
        for pat in (r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"',
                    r'<meta[^>]+property="og:description"[^>]+content="([^"]*)"',
                    r"<title[^>]*>(.*?)</title>"):
            m = re.search(pat, page, re.I | re.S)
            if m and m.group(1).strip():
                return _strip_tags(m.group(1))[:200]
    except Exception:
        pass
    return ""


def topic_of(title, url):
    text = f" {title.lower()} {url.lower()} "
    scores = {t: sum(text.count(k) for k in kws) for t, kws in TOPICS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else f"🔗 Otros ({_domain(url)})"


def enrich(db, include_noted=False, limit=None, get=requests.get, pause=0.5):
    items = rag.load_items(db)
    urls = []
    for it in items:
        if it["urls"] and (include_noted or "link_sin_nota" in it["flags"]):
            urls += [u for u in it["urls"] if u not in urls]
    # Skip links with a title, and failed ones tried in the last week (sites down, blocked, offline).
    retry_after = (datetime.now() - timedelta(days=7)).isoformat()
    known = {r["url"] for r in db.execute("SELECT url FROM links WHERE title != '' OR fetched > ?", (retry_after,))}
    todo = [u for u in urls if u not in known][:limit]
    for i, url in enumerate(todo, 1):
        title = fetch_title(url, get)
        db.execute("INSERT OR REPLACE INTO links VALUES (?,?,?,?)",
                   (url, title, topic_of(title, url), datetime.now().isoformat()))
        print(f"  [{i}/{len(todo)}] {_domain(url)} → {title[:70] or 'sin título'}")
        if pause:
            time.sleep(pause)
    db.commit()
    rag.rebuild(db)   # titles become searchable
    return len(todo)


def report(db):
    items = {u: it for it in rag.load_items(db) for u in it["urls"]}
    groups = defaultdict(list)
    for r in db.execute("SELECT * FROM links"):
        it = items.get(r["url"])
        if it and "link_sin_nota" in it["flags"]:
            groups[r["topic"]].append((it["date"], r["title"], r["url"], it["chat"]))
    lines = [f"# Links sin nota por tema — {datetime.now():%Y-%m-%d}", "",
             "Decidí por grupo: ¿lo voy a usar esta semana? Si no, borralo del chat.", ""]
    for topic, rows in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines += [f"## {topic} ({len(rows)})", ""]
        for date, title, url, chat in sorted(rows, reverse=True):
            lines.append(f"- {title or '_sin título_'} — {url.split('?')[0]}  _({chat}, {date[:10]})_")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    return {t: len(r) for t, r in groups.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="also links that already have a note")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    rag.wd.load_config()
    db = rag.connect()
    rag.refresh_from_bridge(db)
    n = enrich(db, args.all, args.limit)
    groups = report(db)
    print(f"\n  {n} links nuevos consultados · {sum(groups.values())} sin nota en {len(groups)} temas → {OUT}")


if __name__ == "__main__":
    main()
