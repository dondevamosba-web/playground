#!/usr/bin/env python3
"""
Create the "Remodel — España 3175" Google Sheet: expense tracking + vendor quotes
for the Olavarría house renovation (budget: USD 10,000).

Tabs:
  Gastos       — every peso/dollar actually spent
  Presupuestos — vendor quotes to compare before committing
  Resumen      — budget vs spent per room (formulas)

Run once; saves the sheet ID to .env as REMODEL_SHEET_ID.

Usage:
  python3 tools/setup_remodel_sheet.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sheets_client import get_services

BUDGET_USD = 10000

ROOMS = ["Living", "Cocina", "Baños", "Terraza/Pérgola", "Iluminación",
         "Exterior/Fachada", "Dormitorios", "General"]

GASTOS_HEADER = ["Fecha", "Ambiente", "Ítem", "Proveedor/Vendedor",
                 "Presupuestado USD", "Pagado USD", "Pagado ARS",
                 "Medio de pago", "Notas"]

PRESUPUESTOS_HEADER = ["Fecha", "Proveedor", "Ambiente", "Trabajo/Ítem",
                       "Precio USD", "Precio ARS", "Estado (pedido/recibido/elegido/descartado)",
                       "Notas"]


def main():
    sheets, drive = get_services()

    body = {
        "properties": {"title": "Remodel — España 3175"},
        "sheets": [
            {"properties": {"title": "Gastos"}},
            {"properties": {"title": "Presupuestos"}},
            {"properties": {"title": "Resumen"}},
        ],
    }
    ss = sheets.spreadsheets().create(body=body).execute()
    sid = ss["spreadsheetId"]

    resumen_rows = [["Presupuesto total USD", BUDGET_USD],
                    ["Gastado USD", "=SUM(Gastos!F2:F)"],
                    ["Disponible USD", "=B1-B2"],
                    [],
                    ["Ambiente", "Gastado USD"]]
    resumen_rows += [[room, f'=SUMIF(Gastos!B:B,"{room}",Gastos!F:F)'] for room in ROOMS]

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "USER_ENTERED", "data": [
            {"range": "Gastos!A1", "values": [GASTOS_HEADER]},
            {"range": "Presupuestos!A1", "values": [PRESUPUESTOS_HEADER]},
            {"range": "Resumen!A1", "values": resumen_rows},
        ]},
    ).execute()

    env_path = ROOT / ".env"
    env = env_path.read_text()
    if "REMODEL_SHEET_ID" not in env:
        env_path.write_text(env.rstrip("\n") +
                            f"\n\n# Olavarría house remodel tracker\nREMODEL_SHEET_ID={sid}\n")

    print(f"Created: https://docs.google.com/spreadsheets/d/{sid}/edit")
    print("Saved REMODEL_SHEET_ID to .env")


if __name__ == "__main__":
    main()
