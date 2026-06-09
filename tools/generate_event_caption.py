#!/usr/bin/env python3
"""
Generate Instagram captions for electronic party events using Claude.
Produces a feed caption and a shorter story caption per event.

Usage:
  python3 tools/generate_event_caption.py --event-json '{"name":"...", ...}'
  python3 tools/generate_event_caption.py --input .tmp/ra_events.json         # batch
  python3 tools/generate_event_caption.py --input .tmp/ra_events.json --output .tmp/captioned_events.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools.claude_call import call_claude

SYSTEM_PROMPT = """Sos un copywriter para una cuenta de Instagram de fiestas electrónicas en Argentina.
Tu voz es underground, directa, no corporativa. Escribís en español rioplatense.

Reglas de estilo:
- Nunca empieces una oración con ¿ (sin signo de apertura de interrogación)
- Sin emojis al principio de la oración
- Formato fechas argentino: sábado 7 de junio, no June 7
- Horarios con h: 23h, no 11pm
- Tono: conciso, con onda, evocador. Nada de "¡No te lo pierdas!"
- Hashtags en español cuando sea posible

Para el feed caption: 3–5 oraciones. Incluí nombre del evento, fecha, venue y artistas principales. Terminá con hashtags relevantes en una línea aparte.
Para el story caption: 1–2 líneas muy cortas y directas. Sin hashtags. Puede ser una sola pregunta o declaración impactante."""

BATCH_SIZE = 8


def _event_block(event: dict) -> str:
    artists = ", ".join(event.get("artists") or []) or "lineup TBC"
    return (
        f"Nombre: {event.get('name', 'N/A')}\n"
        f"Fecha: {event.get('date', 'N/A')}\n"
        f"Hora: {event.get('time', 'N/A')}\n"
        f"Venue: {event.get('venue', 'N/A')}\n"
        f"Ciudad: {event.get('city', 'Buenos Aires')}\n"
        f"Artistas: {artists}\n"
        f"Precio: {event.get('price', 'N/A')}"
    )


def generate_captions_batch(events: list[dict]) -> list[dict]:
    """Generate captions for a batch of events in a single Claude call."""
    blocks = "\n\n---\n\n".join(
        f"[{i}]\n{_event_block(e)}" for i, e in enumerate(events)
    )
    prompt = (
        f"Generá captions para los siguientes {len(events)} eventos.\n"
        "Respondé SOLO con un JSON array válido, sin texto adicional, con un objeto por evento en orden:\n"
        '[{"feed_caption": "...", "story_caption": "..."}, ...]\n\n'
        f"{blocks}"
    )

    raw = call_claude(prompt, system_prompt=SYSTEM_PROMPT, model="haiku")

    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON array
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Last resort: return empty dicts so caller can degrade gracefully
    return [{"feed_caption": "", "story_caption": ""} for _ in events]


def generate_caption(event: dict) -> dict:
    """Generate captions for a single event."""
    results = generate_captions_batch([event])
    return results[0] if results else {"feed_caption": "", "story_caption": ""}


def main():
    parser = argparse.ArgumentParser(description="Generate IG captions for events")
    parser.add_argument("--event-json", help="Single event as JSON string")
    parser.add_argument("--input", help="Path to JSON array of events (e.g. .tmp/ra_events.json)")
    parser.add_argument("--output", default=".tmp/captioned_events.json")
    args = parser.parse_args()

    if args.event_json:
        event = json.loads(args.event_json)
        captions = generate_caption(event)
        print(json.dumps(captions, indent=2, ensure_ascii=False))
        return

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            events = json.load(f)

        enriched = []
        for start in range(0, len(events), BATCH_SIZE):
            batch = events[start:start + BATCH_SIZE]
            end = start + len(batch)
            print(f"Generating captions {start + 1}–{end}/{len(events)}...")
            captions_list = generate_captions_batch(batch)
            for event, captions in zip(batch, captions_list):
                enriched.append({**event, **captions})

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)

        print(f"\nDone → {args.output}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
