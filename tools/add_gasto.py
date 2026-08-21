#!/usr/bin/env python3
"""
Append an expense (or income) to the Gastos Final sheet, in the right monthly tab.

Usage:
    python tools/add_gasto.py --desc "Pizza" --ars 12000 --category Food --payment "Cash ARS"
    python tools/add_gasto.py --desc "Spotify" --usd 6 --day 15 --month "Jun 2026"
    python tools/add_gasto.py --desc "Basecoat" --usd 3000 --income

Defaults: today's day and current month tab. Also appends a row to the
💸 Gastos Log sheet for audit.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sheets_client import get_services

SID = "1D8s8e2-2RuUz2zlPKYM8Z7wcB7Xc5MCMOVqYNu5j1XY"
LOG_SID = "1yHywdK6bfDBE4s2hOE3cT98q2yvikQZMaFysGGFhdpA"

CATS = ["Food", "Super", "Transport", "Casa", "Salud", "Personal",
        "Salidas", "Tecno", "Otro"]
PAYS = ["Cash ARS", "Cash USD", "MercadoPago", "Wise", "Tarjeta",
        "Transferencia"]


def find_section(vals, header_text):
    """Return (header_row, total_row) 1-based for a section."""
    hdr = total = None
    for i, row in enumerate(vals, 1):
        v = str(row[0]) if row else ""
        if header_text in v:
            hdr = i + 1  # column-header row follows the section title
        elif hdr and v.strip().startswith("TOTAL") and i > hdr:
            total = i
            break
    return hdr, total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--desc", required=True)
    p.add_argument("--ars", type=float)
    p.add_argument("--usd", type=float)
    p.add_argument("--day", default=f"{date.today().day:02d}")
    p.add_argument("--month", default=date.today().strftime("%b %Y"))
    p.add_argument("--category", default="", choices=CATS + [""])
    p.add_argument("--payment", default="", choices=PAYS + [""])
    p.add_argument("--income", action="store_true",
                   help="log under INGRESOS instead of GASTOS DEL MES")
    args = p.parse_args()
    if args.ars is None and args.usd is None:
        p.error("need --ars or --usd")

    sheets, _ = get_services()
    tab = args.month
    vals = sheets.spreadsheets().values().get(
        spreadsheetId=SID, range=f"'{tab}'!A1:G60").execute().get("values", [])
    if not vals:
        sys.exit(f"Tab '{tab}' not found or empty — create the month first.")

    section = "▲ INGRESOS" if args.income else "GASTOS DEL MES"
    hdr, total = find_section(vals, section)
    if not hdr or not total:
        sys.exit(f"Could not locate {section} in '{tab}'")

    # first empty row between header and total
    target = None
    for r in range(hdr + 1, total):
        row = vals[r - 1] if r <= len(vals) else []
        if not row or not any(str(c).strip() for c in row[1:5]):
            target = r
            break
    if target is None:
        sys.exit(f"No empty rows left in {section} of '{tab}'")

    n = target - hdr
    if args.income:
        row_vals = [[n, "", args.desc, args.ars or "", args.usd or ""]]
        rng = f"'{tab}'!A{target}:E{target}"
    else:
        usd = args.usd if args.usd is not None else f"=IF(D{target}>0;D{target}/B$2;\"\")"
        row_vals = [[n, args.day, args.desc, args.ars or "", usd,
                     args.category, args.payment]]
        rng = f"'{tab}'!A{target}:G{target}"
    sheets.spreadsheets().values().update(
        spreadsheetId=SID, range=rng, valueInputOption="USER_ENTERED",
        body={"values": row_vals}).execute()

    # audit log
    from datetime import datetime
    sheets.spreadsheets().values().append(
        spreadsheetId=LOG_SID, range="Log!A1", valueInputOption="USER_ENTERED",
        body={"values": [[datetime.now().isoformat(), tab,
                          "income" if args.income else "daily", args.day,
                          args.desc, args.ars or "", args.usd or "",
                          args.category, args.payment, "ok"]]}).execute()
    print(f"Added to '{tab}' {section} row {target}: {args.desc}")


if __name__ == "__main__":
    main()
