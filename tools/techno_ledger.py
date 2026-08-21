#!/usr/bin/env python3
"""
Techno Apple stock + sales ledger in Google Sheets.

Usage:
  python tools/techno_ledger.py setup                      # create the sheet (one-time)
  python tools/techno_ledger.py add "iPhone 16 128GB" 850  # bought: product, provider cost USD
  python tools/techno_ledger.py add "PS5 Slim" 480 --price 560   # override sell price
  python tools/techno_ledger.py sell 3                     # mark row 3 sold today
  python tools/techno_ledger.py sell 3 --buyer "Juan" --sold-for 930
  python tools/techno_ledger.py list                       # show stock + totals

Sell price defaults to cost + 70 USD (house rule). Sheet ID cached in .env as TECHNO_LEDGER_ID.
NOTE: provider costs live only in this private sheet — never publish them.
"""
import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sheets_client import get_services

MARKUP = 70
ENV_FILE = ROOT / ".env"
ENV_KEY = "TECHNO_LEDGER_ID"
TAB = "Ledger"
HEADERS = ["Fecha compra", "Producto", "Costo USD", "Precio venta USD",
           "Estado", "Fecha venta", "Vendido por USD", "Comprador", "Margen USD"]


def get_sheet_id():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith(f"{ENV_KEY}="):
                return line.split("=", 1)[1].strip()
    return None


def save_sheet_id(sid):
    with open(ENV_FILE, "a") as f:
        f.write(f"\n{ENV_KEY}={sid}\n")


def setup(sheets):
    body = {"properties": {"title": "Techno Apple — Stock y Ventas"},
            "sheets": [{"properties": {"title": TAB}}]}
    ss = sheets.spreadsheets().create(body=body).execute()
    sid = ss["spreadsheetId"]
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range=f"{TAB}!A1", valueInputOption="RAW",
        body={"values": [HEADERS]}).execute()
    save_sheet_id(sid)
    print(f"Created: https://docs.google.com/spreadsheets/d/{sid}")
    return sid


def rows(sheets, sid):
    res = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range=f"{TAB}!A2:I").execute()
    return res.get("values", [])


def add(sheets, sid, product, cost, price):
    price = price if price is not None else cost + MARKUP
    row = [str(date.today()), product, cost, price, "EN STOCK", "", "", "", ""]
    sheets.spreadsheets().values().append(
        spreadsheetId=sid, range=f"{TAB}!A:I", valueInputOption="USER_ENTERED",
        body={"values": [row]}).execute()
    print(f"Agregado: {product} — costo {cost} USD, venta {price} USD")


def sell(sheets, sid, row_num, buyer, sold_for):
    data = rows(sheets, sid)
    idx = row_num - 1
    if idx < 0 or idx >= len(data):
        sys.exit(f"Fila {row_num} no existe (hay {len(data)} items; usá 'list')")
    r = data[idx] + [""] * (9 - len(data[idx]))
    if r[4] == "VENDIDO":
        sys.exit(f"Fila {row_num} ({r[1]}) ya está vendida")
    final = sold_for if sold_for is not None else float(r[3])
    margin = final - float(r[2])
    update = [r[0], r[1], r[2], r[3], "VENDIDO", str(date.today()), final, buyer or "", margin]
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range=f"{TAB}!A{row_num + 1}:I{row_num + 1}",
        valueInputOption="USER_ENTERED", body={"values": [update]}).execute()
    print(f"Vendido: {r[1]} por {final} USD — margen {margin:.0f} USD")


def list_items(sheets, sid):
    data = rows(sheets, sid)
    stock, sold_margin, sold_n = [], 0.0, 0
    for i, r in enumerate(data, 1):
        r = r + [""] * (9 - len(r))
        if r[4] == "EN STOCK":
            stock.append((i, r))
        elif r[4] == "VENDIDO":
            sold_n += 1
            sold_margin += float(r[8] or 0)
    print(f"EN STOCK ({len(stock)}):")
    for i, r in enumerate([s[1] for s in stock]):
        n = stock[i][0]
        print(f"  {n:>3}. {r[1]:<35} costo {r[2]:>6} → venta {r[3]:>6} USD  (desde {r[0]})")
    invested = sum(float(r[2]) for _, r in stock)
    print(f"\nCapital en stock: {invested:.0f} USD · Vendidos: {sold_n} · Margen acumulado: {sold_margin:.0f} USD")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    a = sub.add_parser("add")
    a.add_argument("product")
    a.add_argument("cost", type=float)
    a.add_argument("--price", type=float)
    s = sub.add_parser("sell")
    s.add_argument("row", type=int)
    s.add_argument("--buyer")
    s.add_argument("--sold-for", type=float)
    sub.add_parser("list")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = get_sheet_id()
    if args.cmd == "setup":
        if sid:
            sys.exit(f"Ya existe: https://docs.google.com/spreadsheets/d/{sid}")
        setup(sheets)
        return
    if not sid:
        sys.exit("No hay sheet. Corré primero: python tools/techno_ledger.py setup")
    if args.cmd == "add":
        add(sheets, sid, args.product, args.cost, args.price)
    elif args.cmd == "sell":
        sell(sheets, sid, args.row, args.buyer, args.sold_for)
    elif args.cmd == "list":
        list_items(sheets, sid)


if __name__ == "__main__":
    main()
