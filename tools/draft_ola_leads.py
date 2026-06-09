#!/usr/bin/env python3
"""
Pull new Ola Digital website lead submissions from Netlify and create Gmail drafts.
Each draft is addressed TO the lead — ready for Guido to review and send.

Usage:
  python3 tools/draft_ola_leads.py
  python3 tools/draft_ola_leads.py --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT      = Path(__file__).parent.parent
SEEN_FILE = ROOT / ".tmp" / "ola_leads_seen.json"

load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "tools"))

from gmail_draft import create_draft
from sheets_client import get_services

LEADS_SHEET_ENV = "LEADS_SHEET_ID"
# Columns: submitted_at, nombre, email, negocio, telefono, servicio, mensaje
COL_TS      = 0
COL_NOMBRE  = 1
COL_EMAIL   = 2
COL_NEGOCIO = 3
COL_TEL     = 4
COL_SERVICIO= 5
COL_MENSAJE = 6

OLA_SIGNATURE_HTML = """
<div style="margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <p style="margin:0;font-size:14px;font-weight:600;color:#0E1116;">Guido Carminatti</p>
  <p style="margin:4px 0 0;font-size:13px;color:#6b7280;">
    <a href="https://oladigital.com.ar" style="color:#0EA5E9;text-decoration:none;">OLA Digital</a>
    &nbsp;·&nbsp; Olavarría, Buenos Aires
    &nbsp;·&nbsp;
    <a href="https://wa.me/5491162310105" style="color:#6b7280;text-decoration:none;">WhatsApp</a>
  </p>
</div>"""


def load_seen() -> set:
    return set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()


def save_seen(ids: set):
    SEEN_FILE.parent.mkdir(exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(ids), indent=2))


def get_leads(sheets, sheet_id: str) -> list[dict]:
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:G1000"
    ).execute().get("values", [])

    leads = []
    for row in rows:
        def c(i): return row[i].strip() if i < len(row) else ""
        leads.append({
            "id":       c(COL_TS),
            "name":     c(COL_NOMBRE),
            "email":    c(COL_EMAIL),
            "business": c(COL_NEGOCIO),
            "phone":    c(COL_TEL),
            "service":  c(COL_SERVICIO),
            "message":  c(COL_MENSAJE),
        })
    return leads


def build_email_html(lead: dict) -> str:
    first = lead["name"].split()[0] if lead["name"] else "ahí"
    service_line = (
        f" sobre {lead['service']}"
        if lead["service"] and "diagnóstico" not in lead["service"].lower()
        else ""
    )

    paragraphs = [
        f"Hola {first},",
        "",
        f"Vi que completaste el formulario en oladigital.com.ar{service_line} — gracias por escribir.",
        "",
        "Me gustaría entender mejor tu negocio para ver cómo podemos ayudarte a crecer. "
        "¿Podemos coordinar una llamada corta de 20 minutos esta semana?",
        "",
        "Escribime por WhatsApp y lo organizamos: https://wa.me/5491162310105",
        "",
        "¡Espero tu respuesta!",
    ]

    body_html = "".join(
        f"<p style='margin:0 0 10px;font-family:-apple-system,sans-serif;"
        f"font-size:15px;line-height:1.6;color:#0E1116;'>{line}</p>"
        if line else "<br>"
        for line in paragraphs
    )
    return f"<div>{body_html}{OLA_SIGNATURE_HTML}</div>"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheet_id = os.getenv(LEADS_SHEET_ENV)
    if not sheet_id:
        print(f"ERROR: {LEADS_SHEET_ENV} not set in .env")
        sys.exit(1)

    seen = load_seen()
    sheets, _ = get_services()
    leads = get_leads(sheets, sheet_id)

    new_leads = [l for l in leads if l["id"] not in seen]
    print(f"  {len(leads)} total leads, {len(new_leads)} new")

    if not new_leads:
        print("No new leads.")
        return

    drafted = 0
    for lead in new_leads:
        seen.add(lead["id"])

        if not lead["email"]:
            print(f"  SKIP (no email): {lead['id']}")
            continue

        print(f"  Drafting → {lead['name'] or '(no name)'} <{lead['email']}>")
        if lead["message"]:
            print(f"    '{lead['message'][:80]}'")

        if not args.dry_run:
            result = create_draft(
                to=lead["email"],
                subject="Re: Tu consulta en OLA Digital",
                body=build_email_html(lead),
                html=True,
            )
            print(f"    Draft ID: {result['draft_id']}")

        drafted += 1

    if not args.dry_run:
        save_seen(seen)

    action = "[dry-run] Would create" if args.dry_run else "Created"
    print(f"\n{action} {drafted} Gmail draft(s).")


if __name__ == "__main__":
    main()
