#!/usr/bin/env python3
"""
Reorganize the '💰📊 Cash + Big Buys' tab of the Gastos Final sheet.
Keeps all existing data, lays it out in clean sections. Backup of the old
grid is in .tmp/cash_tab_backup.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sheets_client import get_services

SID = "1D8s8e2-2RuUz2zlPKYM8Z7wcB7Xc5MCMOVqYNu5j1XY"
TAB = "💰📊 Cash + Big Buys"
TAB_ID = 896915073

# Sheet locale uses ';' as formula separator and ',' as decimal mark.
def usd_formula(row, amount_col, cur_col):
    return (f'=IF({cur_col}{row}="USD";{amount_col}{row};'
            f'IF({cur_col}{row}="ARS";{amount_col}{row}/B$3;'
            f'IF({cur_col}{row}="EUR";{amount_col}{row}*1,08;"")))')

rows = [[] for _ in range(60)]

def put(r, c, vals):
    row = rows[r - 1]
    while len(row) < c - 1 + len(vals):
        row.append("")
    for i, v in enumerate(vals):
        row[c - 1 + i] = v

# ── LEFT BLOCK (A–E) ──────────────────────────────────────────────
put(1, 1, ["💰 CASH ASSETS — JUN 2026"])
put(2, 1, ["Account", "Balance", "Cur", "Notes", "≈ USD"])
put(3, 1, ["USD/ARS Rate", 1400, "", "← update this rate", ""])
assets = [
    ("Wise (USD)", 15000, "USD", ""),
    ("USD Cash (Olav)", 323, "USD", ""),
    ("EUR Cash (Olav)", 594, "EUR", "× 1.08 USD/EUR"),
    ("Binance USDT", 0, "USD", ""),
    ("Base Jun", 2600, "USD", ""),
    ("Casa", 65000, "USD", ""),
    ("Mercadopago", 300000, "ARS", "÷ rate"),
    ("Terreno (land)", 35000, "USD", ""),
    ("FABI", 2000, "USD", ""),
    ("Level", 300, "USD", ""),
]
for i, (name, bal, cur, note) in enumerate(assets):
    r = 4 + i
    put(r, 1, [name, bal, cur, note, usd_formula(r, "B", "C")])
put(14, 1, ["TOTAL ≈ USD", "", "", "", "=SUM(E4:E13)"])

put(16, 1, ["▼ GASTOS FUTUROS"])
put(17, 1, ["Item", "Amount", "Cur", "Notes", "≈ USD"])
futuros = [("Vazquez", 1800), ("Erramouspe", 1300), ("Papa", 500)]
for i, (name, amt) in enumerate(futuros):
    r = 18 + i
    put(r, 1, [name, amt, "USD", "", usd_formula(r, "B", "C")])
put(21, 1, ["TOTAL FUTUROS", "", "", "", "=SUM(E18:E20)"])

put(23, 1, ["📊 NETOS"])
put(24, 1, ["Total activos", "", "", "", "=E14"])
put(25, 1, ["− Gastos futuros", "", "", "", "=E21"])
put(26, 1, ["NETO ≈ USD", "", "", "", "=E24-E25"])
put(27, 1, ["Total sin inmuebles (sin casa+terreno)", "", "", "", "=E14-E9-E11"])
put(28, 1, ["− Gastos futuros", "", "", "", "=E21"])
put(29, 1, ["NETO sin inmuebles", "", "", "", "=E27-E28"])

put(31, 1, ["💳 DEUDAS"])
put(32, 1, ["A quién", "Item", "Amount", "Cur", "≈ USD"])
deudas = [
    ("Anto", "Super Carrefour", 35000, "ARS"),
    ("Anto", "Lavado de auto", 15000, "ARS"),
    ("Anto", "Luz", 70000, "ARS"),
    ("Anto", "Ganga", 25000, "ARS"),
    ("Anto", "Starlink", 20000, "ARS"),
    ("Anto", "Tarjetas Jun", "", "ARS"),
    ("Anto", "Bari", 115, "USD"),
    ("Diana Campos (psicóloga)", "Deuda", 150000, "ARS"),
]
for i, (who, item, amt, cur) in enumerate(deudas):
    r = 33 + i
    put(r, 1, [who, item, amt, cur, usd_formula(r, "C", "D")])
put(41, 1, ["TOTAL DEUDAS ≈ USD", "", "", "", "=SUM(E33:E40)"])

put(43, 1, ["🏠 CASA"])
put(44, 1, ["Item", "Amount"])
casa = [("Voy", 6500), ("2do pago", 26000), ("3ero falta", 32500),
        ("Cash en casa", 34000)]
for i, (item, amt) in enumerate(casa):
    put(45 + i, 1, [item, amt])
put(49, 1, ["Subtotal", "=SUM(B45:B48)"])

# ── RIGHT BLOCK (G–M) ─────────────────────────────────────────────
put(1, 7, ["🛍 BIG BUYS — ALL TIME"])
put(2, 7, ["Month", "Date", "Item", "Amount", "Cur", "≈ USD", "Notes"])
big_buys = [
    ("oct 2023", "01/10", "1er Pago Cabaña", 50000, "ARS", ""),
    ("oct 2023", "03/10", "2do Pago Cabaña", 118000, "ARS", ""),
    ("oct 2023", "05/10", "Iphone Gonza CF 13Pro", 105, "USD", ""),
    ("nov 2023", "07/10", "D Dani (deuda)", 500, "USD", ""),
    ("nov 2023", "09/10", "HSBC pago", 275, "USD", ""),
    ("mar 2025", "11/10", "MSI Cyborg laptop", 810, "USD", ""),
    ("mar 2025", "13/10", "Sillon", 230000, "ARS", ""),
    ("mar 2025", "15/10", "Monitor", 250000, "ARS", ""),
    ("nov 2025", "17/10", "Sur Pesca", 350000, "ARS", ""),
    ("nov 2025", "19/10", "Chapa", 250000, "ARS", ""),
    ("nov 2025", "21/10", "Regalo Guido", 150000, "ARS", ""),
    ("apr 2026", "23/10", "Gastos Abril (varios)", 1466.67, "USD", "Big month"),
    ("may 2026", "19/05", "PS5 Joystick (DualSense)", 95, "USD", ""),
]
for i, (month, date, item, amt, cur, note) in enumerate(big_buys):
    r = 3 + i
    put(r, 7, [month, date, item, amt, cur, usd_formula(r, "J", "K"), note])
put(16, 7, ["TOTAL GASTADO", "", "", "", "", "=SUM(L3:L15)"])

put(18, 7, ["📅 BCM 2026"])
put(19, 7, ["Month", "Amount USD"])
bcm = ["Julio BCM", "Septiembre BCM", "Octubre BCM", "Noviembre BCM",
       "Diciembre BCM"]
for i, m in enumerate(bcm):
    put(20 + i, 7, [m, 1800])
put(25, 7, ["Total BCM", "=SUM(H20:H24)"])
put(27, 7, ["Total 2026 (neto sin inmuebles + BCM)", "=E29+H25"])

# ── WRITE ─────────────────────────────────────────────────────────
sheets, _ = get_services()

# Clear all values and formatting in the old grid
sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
    {"updateCells": {
        "range": {"sheetId": TAB_ID, "startRowIndex": 0, "endRowIndex": 60,
                  "startColumnIndex": 0, "endColumnIndex": 20},
        "fields": "userEnteredValue,userEnteredFormat"}}
]}).execute()

sheets.spreadsheets().values().update(
    spreadsheetId=SID, range=f"'{TAB}'!A1",
    valueInputOption="USER_ENTERED", body={"values": rows}).execute()

# ── FORMAT ────────────────────────────────────────────────────────
NAVY = {"red": 0.10, "green": 0.10, "blue": 0.18}
BLUE = {"red": 0.06, "green": 0.20, "blue": 0.38}
YELL = {"red": 0.96, "green": 0.65, "blue": 0.14}
GRAY = {"red": 0.96, "green": 0.96, "blue": 0.97}
RED = {"red": 0.91, "green": 0.30, "blue": 0.24}
GREEN = {"red": 0.15, "green": 0.68, "blue": 0.38}
WHITE = {"red": 1, "green": 1, "blue": 1}


def band(r, c1, c2, bg, fg=WHITE, bold=True):
    return {"repeatCell": {
        "range": {"sheetId": TAB_ID, "startRowIndex": r - 1, "endRowIndex": r,
                  "startColumnIndex": c1 - 1, "endColumnIndex": c2},
        "cell": {"userEnteredFormat": {
            "backgroundColor": bg,
            "textFormat": {"foregroundColor": fg, "bold": bold}}},
        "fields": "userEnteredFormat(backgroundColor,textFormat)"}}


def numfmt(r1, r2, c1, c2, pattern):
    return {"repeatCell": {
        "range": {"sheetId": TAB_ID, "startRowIndex": r1 - 1, "endRowIndex": r2,
                  "startColumnIndex": c1 - 1, "endColumnIndex": c2},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "NUMBER", "pattern": pattern}}},
        "fields": "userEnteredFormat.numberFormat"}}


USD_PAT = '"$"#,##0.00'
ARS_PAT = "#,##0"

reqs = [
    # section titles
    band(1, 1, 5, NAVY), band(16, 1, 5, NAVY), band(23, 1, 5, NAVY),
    band(31, 1, 5, RED), band(43, 1, 5, NAVY),
    band(1, 7, 13, NAVY), band(18, 7, 13, NAVY),
    # table headers
    band(2, 1, 5, BLUE), band(17, 1, 5, BLUE), band(32, 1, 5, BLUE),
    band(44, 1, 2, BLUE), band(2, 7, 13, BLUE), band(19, 7, 8, BLUE),
    # rate row
    band(3, 1, 5, YELL, fg=NAVY),
    # totals
    band(14, 1, 5, GREEN), band(21, 1, 5, YELL, fg=NAVY),
    band(26, 1, 5, GREEN), band(29, 1, 5, GREEN),
    band(41, 1, 5, RED), band(49, 1, 2, YELL, fg=NAVY),
    band(16, 7, 13, GREEN), band(25, 7, 8, YELL, fg=NAVY),
    band(27, 7, 13, GREEN),
    # alternating-friendly light fill on data areas
    {"repeatCell": {
        "range": {"sheetId": TAB_ID, "startRowIndex": 3, "endRowIndex": 13,
                  "startColumnIndex": 0, "endColumnIndex": 5},
        "cell": {"userEnteredFormat": {"backgroundColor": GRAY}},
        "fields": "userEnteredFormat.backgroundColor"}},
    # number formats: amount columns raw, ≈USD columns as dollars
    numfmt(4, 13, 2, 2, ARS_PAT), numfmt(4, 29, 5, 5, USD_PAT),
    numfmt(33, 41, 3, 3, ARS_PAT), numfmt(33, 41, 5, 5, USD_PAT),
    numfmt(45, 49, 2, 2, ARS_PAT),
    numfmt(3, 15, 10, 10, ARS_PAT), numfmt(3, 16, 12, 12, USD_PAT),
    numfmt(20, 25, 8, 8, USD_PAT), numfmt(27, 27, 8, 8, USD_PAT),
    # column widths
    {"updateDimensionProperties": {
        "range": {"sheetId": TAB_ID, "dimension": "COLUMNS",
                  "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 240}, "fields": "pixelSize"}},
    {"updateDimensionProperties": {
        "range": {"sheetId": TAB_ID, "dimension": "COLUMNS",
                  "startIndex": 8, "endIndex": 9},
        "properties": {"pixelSize": 200}, "fields": "pixelSize"}},
    {"updateDimensionProperties": {
        "range": {"sheetId": TAB_ID, "dimension": "COLUMNS",
                  "startIndex": 5, "endIndex": 6},
        "properties": {"pixelSize": 30}, "fields": "pixelSize"}},
]
sheets.spreadsheets().batchUpdate(spreadsheetId=SID,
                                  body={"requests": reqs}).execute()
print("done")
