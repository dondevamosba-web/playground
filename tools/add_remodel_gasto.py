#!/usr/bin/env python3
"""
Append an expense or a vendor quote to the "Remodel — España 3175" sheet.

Usage:
  # Expense (what you actually paid)
  python3 tools/add_remodel_gasto.py --room Cocina --item "Mesada granito" \
      --vendor "Marmolería Díaz" --usd 450 --pay Efectivo

  # Quote (presupuesto to compare)
  python3 tools/add_remodel_gasto.py --quote --room "Baños" --item "Cambio grifería x2" \
      --vendor "Plomero Juan" --usd 180

Defaults: today's date. ARS amounts via --ars (either or both currencies allowed).
"""
import argparse
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from sheets_client import get_services

ROOMS = ["Living", "Cocina", "Baños", "Terraza/Pérgola", "Iluminación",
         "Exterior/Fachada", "Dormitorios", "General"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--quote", action="store_true", help="log a vendor quote instead of an expense")
    p.add_argument("--room", required=True, choices=ROOMS)
    p.add_argument("--item", required=True)
    p.add_argument("--vendor", default="")
    p.add_argument("--usd", type=float)
    p.add_argument("--ars", type=float)
    p.add_argument("--budgeted-usd", type=float, help="expenses only: what was quoted/expected")
    p.add_argument("--pay", default="", help="expenses only: medio de pago")
    p.add_argument("--status", default="recibido", help="quotes only: pedido/recibido/elegido/descartado")
    p.add_argument("--notes", default="")
    p.add_argument("--date", default=date.today().isoformat())
    args = p.parse_args()

    if not args.usd and not args.ars:
        p.error("set --usd and/or --ars")

    sid = os.environ["REMODEL_SHEET_ID"]
    sheets, _ = get_services()

    if args.quote:
        tab = "🏠 Remodel Presupuestos"
        row = [args.date, args.vendor, args.room, args.item,
               args.usd or "", args.ars or "", args.status, args.notes]
    else:
        tab = "🏠 Remodel Gastos"
        row = [args.date, args.room, args.item, args.vendor,
               args.budgeted_usd or "", args.usd or "", args.ars or "",
               args.pay, args.notes]

    sheets.spreadsheets().values().append(
        spreadsheetId=sid, range=f"'{tab}'!A1",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
    print(f"Added to {tab}: {args.item} ({args.room})")


if __name__ == "__main__":
    main()
