#!/usr/bin/env python3
"""
WhatsApp notes digest — parses exports of the 3 personal note-to-self chats
(Psi 💭, Ide 🎁, Vida 🏠💪) and turns them into one organized digest.

For each message it detects:
  - tag: explicit #hashtag, or inferred from keywords (limited to the chat's tags)
  - kind: link / task / note
  - flags: link without a note, late-night (00–06h), duplicate of an earlier message

Output (in .tmp/whatsapp_digest/):
  digest.json   all messages, classified (the agent loads this into Notion)
  digest.md     human-readable summary: pending tasks, bare links, duplicates

Usage:
  python3 tools/whatsapp_digest.py export1.zip export2.zip export3.zip
  python3 tools/whatsapp_digest.py path/to/folder_with_chat_txt/
  python3 tools/whatsapp_digest.py *.zip --since 2026-09-01
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / ".tmp" / "whatsapp_digest"

CONFIG = OUT / "config.json"  # personal tags/keywords, lives in .tmp/ so it never reaches git

# ── Chat → allowed tags ────────────────────────────────────────────────────────
# The WhatsApp group name starts with the chat key ("Psi", "Ide", "Vida").
# These are generic defaults; CONFIG can override a chat's tags and add keywords:
#   {"chats": {"Psi": {"tags": ["#terapia", "#aprender"]}},
#    "keywords": {"#cliente": ["nombre de cliente"]}, "tag_alias": {"#terapia": "#otro"}}
CHATS = {
    "Psi":  {"name": "Psi 💭",   "tags": ["#terapia", "#aprender"]},
    "Ide":  {"name": "Ide 🎁",   "tags": ["#biz", "#cliente", "#aprender", "#postear", "#plata"]},
    "Vida": {"name": "Vida 🏠💪", "tags": ["#casa", "#compra", "#cuerpo"]},
}
ALIASES = {"Fit": "Vida", "Ideas": "Ide"}
# #aprender lives in Psi and Ide; a misplaced one goes to Ide.
HOME_ORDER = ["Ide", "Vida", "Psi"]

# Keyword → tag, used only when the message has no explicit #tag. Inference looks at
# every tag (not just the chat's), so a purchase noted in Psi gets flagged as misplaced.
KEYWORDS = {
    "#terapia":  ["terapia", "psicólogo", "psicologo", "relación", "relacion", "decisión", "perdón", "extraño",
                  "patrón", "patron", "duelo", "vínculo", "vinculo", "soñé", "llorar"],
    "#cliente":  ["cliente", "clienta", "propuesta", "cotización"],
    "#postear":  ["postear", "subir este", "publica", "insta de", "hacer este"],
    "#plata":    ["usd", "u$", "me debe", "$1", "$2", "$3", "gastos", "precio", "presupuesto"],
    "#biz":      ["ads", "leads", "marketing", "negocio", "página", "pagina", "linktree", "dominio", "agente"],
    "#aprender": ["teach me", "aprender", "tutorial", "repo", "mcp", "claude", "ver esta"],
    "#casa":     ["techo", "cocina", "baño", "bidet", "aberturas", "carpeta", "terraza", "balcón", "balcon",
                  "pintar", "piso", "plano", "durlock", "gasista", "plomero", "sillón", "sillon", "tele",
                  "garage", "dormitorio", "living", "pasillo", "placard", "parrilla"],
    "#compra":   ["comprar", "wishlist", "lista de supermercado", "balanza", "adaptador", "lámpara", "lampara",
                  "campera", "vasos", "tenedores", "bicarbonato", "yerba", "lechuga"],
    "#cuerpo":   ["dental", "bruxismo", "agua", "fitnes", "entrenar", "gym", "comer", "fideos", "foam roller"],
}


def load_config():
    """Merge the personal CONFIG (if present) into CHATS / KEYWORDS."""
    if not CONFIG.exists():
        return
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    for old, new in cfg.get("tag_alias", {}).items():
        KEYWORDS[new] = KEYWORDS.pop(old, [])
        for chat in CHATS.values():
            chat["tags"] = [new if t == old else t for t in chat["tags"]]
    for key, chat in cfg.get("chats", {}).items():
        CHATS.setdefault(key, {"name": key, "tags": []}).update(chat)
    for tag, words in cfg.get("keywords", {}).items():
        KEYWORDS.setdefault(tag, []).extend(words)
    ALIASES.update(cfg.get("aliases", {}))


TASK_VERBS = ("comprar", "hacer", "armar", "buscar", "ir ", "mandar", "mándale", "mandale", "aplicar",
              "escribirle", "cotizar", "conseguir", "arreglar", "agregar", "sacar", "ver ", "postear",
              "subir", "decirle", "charlarlo", "hablar", "invertir", "usar ", "averiguar", "probar")

SKIP = ("Eliminaste este mensaje", "<imagen omitida>", "<Mensaje de album>", "<documento omitido>",
        "<video omitido>", "<mensaje de voz omitido>", "[Notificación del sistema]")

LINE_RE = re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}:\d{2}\s?[AP]M)\] (.+?): (.*)$")
SYSTEM_RE = re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}:\d{2}\s?[AP]M)\] - ")
URL_RE = re.compile(r"https?://\S+")
TAG_RE = re.compile(r"#[a-záéíóúñ]+", re.IGNORECASE)
NAME_RE = re.compile(r"Exportación de chat de WhatsApp: (.+)")


# ── Loading ────────────────────────────────────────────────────────────────────

def _chat_key(title):
    first = re.split(r"[\s_]", title.strip(), maxsplit=1)[0]
    key = ALIASES.get(first, first)
    return key if key in CHATS else None


def _load_sources(paths):
    """Yield (chat_title, chat.txt text) for each zip / folder / txt given."""
    for raw in paths:
        p = Path(raw)
        if p.suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                names = z.namelist()
                txt = next((n for n in names if n.endswith(".txt")), None)
                md = next((n for n in names if n.endswith(".md")), None)
                if not txt:
                    print(f"  ⚠ {p.name}: no .txt inside, skipped")
                    continue
                title = _title_from_md(z.read(md).decode("utf-8")) if md else None
                yield title or p.stem, z.read(txt).decode("utf-8")
        elif p.is_dir():
            for txt in sorted(p.rglob("*.txt")):
                md = txt.with_suffix(".md")
                title = _title_from_md(md.read_text(encoding="utf-8")) if md.exists() else None
                yield title or txt.parent.name, txt.read_text(encoding="utf-8")
        elif p.suffix == ".txt":
            yield p.stem, p.read_text(encoding="utf-8")
        else:
            print(f"  ⚠ {raw}: not a .zip, .txt or folder, skipped")


def _title_from_md(text):
    m = NAME_RE.search(text)
    return m.group(1).strip() if m else None


def parse_chat(text):
    """Return a list of {ts, text} merging multi-line messages."""
    msgs, cur = [], None
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if m:
            if cur:
                msgs.append(cur)
            ts = datetime.strptime(f"{m.group(1)} {m.group(2).replace(' ', ' ')}", "%m/%d/%y %I:%M:%S %p")
            cur = {"ts": ts, "text": m.group(4)}
        elif SYSTEM_RE.match(line):
            if cur:
                msgs.append(cur)
            cur = None
        elif cur is not None:
            cur["text"] += "\n" + line
    if cur:
        msgs.append(cur)
    return [m for m in msgs if not any(m["text"].strip().startswith(s) for s in SKIP) and m["text"].strip()]


# ── Classification ─────────────────────────────────────────────────────────────

def classify(msg, chat_key):
    text = msg["text"].strip()
    low = text.lower()
    allowed = CHATS[chat_key]["tags"]

    tags = [t.lower() for t in TAG_RE.findall(text)]
    tag_source = "explicit" if tags else "inferred"
    if not tags:
        scores = {t: sum(len(re.findall(rf"(?<!\w){re.escape(k)}(?!\w)", low)) for k in KEYWORDS[t])
                  for t in KEYWORDS}
        # Prefer the chat's own tags; only call it misplaced when none of them match.
        own = {t: scores[t] for t in allowed}
        pool = own if any(own.values()) else scores
        best = max(pool, key=pool.get)
        tags = [best] if pool[best] else []

    urls = URL_RE.findall(text)
    note = URL_RE.sub("", text).strip()
    if urls:
        kind = "link"
    elif low.startswith(TASK_VERBS) or "☐" in text:
        kind = "task"
    else:
        kind = "note"

    flags = []
    if urls and not note:
        flags.append("link_sin_nota")
    if msg["ts"].hour < 6:
        flags.append("madrugada")
    if [t for t in tags if t not in allowed]:
        flags.append("fuera_de_lugar")

    return {
        "chat": CHATS[chat_key]["name"],
        "date": msg["ts"].strftime("%Y-%m-%d %H:%M"),
        "tags": tags,
        "tag_source": tag_source,
        "kind": kind,
        "urls": urls,
        "note": note,
        "flags": flags,
    }


def mark_duplicates(items):
    """Flag messages whose text (normalized) already appeared earlier in any chat."""
    seen = {}
    for it in sorted(items, key=lambda x: x["date"]):
        key = re.sub(r"\s+", " ", it["note"].lower())[:200]
        if len(key) < 15:
            continue
        if key in seen:
            it["flags"].append("duplicado")
            it["duplicate_of"] = seen[key]
        else:
            seen[key] = f'{it["chat"]} {it["date"]}'


def unchecked_items(items):
    """Pull ☐ checklist lines from the latest copy of each checklist."""
    latest = {}
    for it in items:
        if "☐" in it["note"]:
            header = it["note"].splitlines()[0].strip()
            if header not in latest or it["date"] > latest[header]["date"]:
                latest[header] = it
    out = []
    for header, it in latest.items():
        for line in it["note"].splitlines():
            if line.strip().startswith("☐"):
                out.append((header, line.strip()[1:].strip(), it["date"]))
    return out


def task_key(title):
    """Stable id for a task, so the same task noted twice (or in two chats) is one task."""
    norm = re.sub(r"[^\w\s]", "", title.lower())
    return hashlib.sha1(re.sub(r"\s+", " ", norm).strip().encode()).hexdigest()[:12]


def pending_items(items):
    """Open checklist lines (latest copy) + loose tasks, deduplicated by task_key."""
    out, seen = [], set()
    by_date = {it["date"]: it for it in items}
    for header, title, date in unchecked_items(items):
        src = by_date[date]
        out.append({"title": title, "tag": (src["tags"] or [""])[0], "chat": src["chat"],
                    "date": date, "source": header})
    for it in items:
        if it["kind"] == "task" and "☐" not in it["note"]:
            out.append({"title": it["note"].splitlines()[0][:120].strip(), "tag": (it["tags"] or [""])[0],
                        "chat": it["chat"], "date": it["date"], "source": "mensaje"})
    result = []
    for p in out:
        p["key"] = task_key(p["title"])
        if p["key"] not in seen:
            seen.add(p["key"])
            result.append(p)
    return result


# ── Report ─────────────────────────────────────────────────────────────────────

def build_markdown(items):
    by_chat = defaultdict(list)
    for it in items:
        by_chat[it["chat"]].append(it)

    lines = [f"# WhatsApp digest — {datetime.now():%Y-%m-%d}", ""]
    lines.append("| Chat | Mensajes | Links | Links sin nota | Tareas | Madrugada | Duplicados | Fuera de lugar |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for chat, its in by_chat.items():
        c = lambda f: sum(1 for i in its if f(i))
        lines.append(f"| {chat} | {len(its)} | {c(lambda i: i['kind'] == 'link')} "
                     f"| {c(lambda i: 'link_sin_nota' in i['flags'])} | {c(lambda i: i['kind'] == 'task')} "
                     f"| {c(lambda i: 'madrugada' in i['flags'])} | {c(lambda i: 'duplicado' in i['flags'])} "
                     f"| {c(lambda i: 'fuera_de_lugar' in i['flags'])} |")

    lines += ["", "## Tags", ""]
    for chat, its in by_chat.items():
        counts = Counter(t for i in its for t in i["tags"])
        untagged = sum(1 for i in its if not i["tags"])
        tag_str = ", ".join(f"{t} {n}" for t, n in counts.most_common())
        lines.append(f"- **{chat}**: {tag_str or '—'} · sin tag: {untagged}")

    misplaced = [it for it in items if "fuera_de_lugar" in it["flags"]]
    lines += ["", f"## Fuera de lugar ({len(misplaced)}) — moverlos al chat que corresponde", ""]
    for it in misplaced:
        dest = next((CHATS[k]["name"] for k in HOME_ORDER if it["tags"][0] in CHATS[k]["tags"]), "?")
        lines.append(f"- {it['note'].splitlines()[0][:80]} — está en {it['chat']}, va a {dest} ({it['tags'][0]})")

    lines += ["", "## Checklists abiertas (última versión)", ""]
    for header, item, date in unchecked_items(items):
        lines.append(f"- [ ] {item}  _({header}, {date[:10]})_")

    lines += ["", "## Tareas sueltas", ""]
    for it in items:
        if it["kind"] == "task" and "☐" not in it["note"] and "duplicado" not in it["flags"]:
            first = it["note"].splitlines()[0][:120]
            lines.append(f"- [ ] {first}  _({it['chat']}, {it['date'][:10]}, {' '.join(it['tags']) or 'sin tag'})_")

    lines += ["", "## Duplicados (copiados en vez de actualizar)", ""]
    for it in items:
        if "duplicado" in it["flags"]:
            lines.append(f"- {it['note'].splitlines()[0][:80]} — {it['chat']} {it['date']} (ya estaba en {it['duplicate_of']})")

    bare = [it for it in items if "link_sin_nota" in it["flags"]]
    lines += ["", f"## Links sin nota ({len(bare)}) — agregales un verbo o borralos", ""]
    for it in bare:
        lines.append(f"- {it['urls'][0].split('?')[0]}  _({it['chat']}, {it['date'][:10]})_")

    return "\n".join(lines) + "\n"


# ── Main ───────────────────────────────────────────────────────────────────────

def utf8_io():
    """Windows pipes default to cp1252, which can't print emojis (🏠 💭): force UTF-8 on stdio."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="WhatsApp export .zip, chat .txt, or folder")
    ap.add_argument("--since", help="only messages from this date (YYYY-MM-DD)")
    args = ap.parse_args()
    utf8_io()
    load_config()

    items = []
    for title, text in _load_sources(args.inputs):
        key = _chat_key(title)
        if not key:
            print(f"  ⚠ '{title}': chat name must start with Psi / Ide / Vida, skipped")
            continue
        msgs = parse_chat(text)
        if not msgs and text.strip():
            print(f"  ⚠ '{title}': 0 mensajes leídos — ¿cambió el formato del export de WhatsApp?")
        if args.since:
            since = datetime.strptime(args.since, "%Y-%m-%d")
            msgs = [m for m in msgs if m["ts"] >= since]
        items += [classify(m, key) for m in msgs]
        print(f"  ✓ {title} → {CHATS[key]['name']}: {len(msgs)} mensajes")

    if not items:
        sys.exit("No messages parsed.")

    items.sort(key=lambda x: x["date"])
    mark_duplicates(items)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "digest.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "digest.md").write_text(build_markdown(items), encoding="utf-8")
    print(f"\n  → {OUT / 'digest.md'}\n  → {OUT / 'digest.json'}  ({len(items)} items)")


if __name__ == "__main__":
    main()
