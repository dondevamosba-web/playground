#!/usr/bin/env python3
"""
Monthly close + mid-month burn check for the Gastos Final sheet.

Usage:
    python tools/gastos_monthly_close.py            # close: create new month tab,
                                                    # add Anual row, net worth snapshot,
                                                    # Gmail draft with summary
    python tools/gastos_monthly_close.py --burn-check   # alert draft if month-to-date
                                                        # egresos > 130% of burn rate

Designed to run on a schedule (1st and 15th of each month).
"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sheets_client import get_services

SID = "1D8s8e2-2RuUz2zlPKYM8Z7wcB7Xc5MCMOVqYNu5j1XY"
ANUAL_ID = 1944016533
EMAIL = "carminattiguido@gmail.com"


def month_label(d):
    return d.strftime("%b %Y")


def prev_month(d):
    return date(d.year - 1, 12, 1) if d.month == 1 else date(d.year, d.month - 1, 1)


def get_total(sheets, tab, label):
    vals = sheets.spreadsheets().values().get(
        spreadsheetId=SID, range=f"'{tab}'!A1:E60",
        valueRenderOption="UNFORMATTED_VALUE").execute().get("values", [])
    for row in vals:
        if row and str(row[0]).strip() == label:
            return float(row[4]) if len(row) > 4 and row[4] != "" else 0.0
    return 0.0


def gmail_draft(subject, body):
    try:
        from gmail_draft import create_draft
        create_draft(EMAIL, subject, body)
        print(f"Gmail draft created: {subject}")
    except Exception as e:
        print(f"WARN: could not create Gmail draft ({e}); summary below:\n{body}")


def burn_check(sheets):
    today = date.today()
    tab = month_label(today)
    var = get_total(sheets, tab, "TOTAL VARIABLE")
    fij = get_total(sheets, tab, "TOTAL FIJOS")
    spent = var + fij
    burn = sheets.spreadsheets().values().get(
        spreadsheetId=SID, range="'📊 Anual'!B40",
        valueRenderOption="UNFORMATTED_VALUE").execute()["values"][0][0]
    expected = burn * today.day / 30
    print(f"{tab}: gastado ${spent:,.0f} vs esperado ${expected:,.0f} (burn ${burn:,.0f}/mes)")
    if spent > expected * 1.3:
        gmail_draft(
            f"⚠️ Gastos {tab}: vas {spent / expected:.0%} del ritmo normal",
            f"Llevás ${spent:,.0f} gastados al día {today.day} de {tab}.\n"
            f"Al ritmo promedio (${burn:,.0f}/mes) deberías ir por ${expected:,.0f}.\n"
            f"Revisá la hoja: https://docs.google.com/spreadsheets/d/{SID}")
    else:
        print("OK — dentro del ritmo normal, no se genera alerta.")


def close_month(sheets):
    today = date.today()
    cur, prev = month_label(today), month_label(prev_month(today))
    meta = sheets.spreadsheets().get(spreadsheetId=SID).execute()
    tabs = {s["properties"]["title"]: s["properties"] for s in meta["sheets"]}
    if cur in tabs:
        print(f"Tab '{cur}' ya existe — skip creación.")
    else:
        src = tabs[prev]
        r = sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
            {"duplicateSheet": {"sourceSheetId": src["sheetId"],
                                "insertSheetIndex": src["index"] + 1,
                                "newSheetName": cur}}]}).execute()
        # clear month-specific data: title, ingresos, salidas wise, gastos del mes
        vals = sheets.spreadsheets().values().get(
            spreadsheetId=SID, range=f"'{cur}'!A1:G60").execute().get("values", [])
        data = [{"range": f"'{cur}'!A1",
                 "values": [[f"💸 {cur.upper()} — GASTOS MENSUALES"]]}]
        in_gastos = False
        for i, row in enumerate(vals, 1):
            v = str(row[0]) if row else ""
            if "GASTOS DEL MES" in v:
                in_gastos = True
            if row and len(row) > 1 and "Salidas Wise" in str(row[1]):
                data.append({"range": f"'{cur}'!E{i}:F{i}", "values": [["", ""]]})
            if in_gastos and v.strip().isdigit() and len(row) > 2 and str(row[2]).strip():
                data.append({"range": f"'{cur}'!B{i}:G{i}", "values": [[""] * 6]})
            if not in_gastos and v.strip().isdigit() and i < 10:  # ingresos
                data.append({"range": f"'{cur}'!C{i}:E{i}", "values": [["", "", ""]]})
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SID,
            body={"valueInputOption": "USER_ENTERED", "data": data}).execute()
        print(f"Tab '{cur}' creada desde '{prev}'.")

    # Anual: add row for the new month above TOTAL if missing
    avals = sheets.spreadsheets().values().get(
        spreadsheetId=SID, range="'📊 Anual'!A1:A60").execute().get("values", [])
    labels = [str(r[0]).lower() if r else "" for r in avals]
    total_r = next(i for i, v in enumerate(labels, 1) if v == "total")
    if cur.lower() not in labels:
        sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
            {"insertDimension": {"range": {
                "sheetId": ANUAL_ID, "dimension": "ROWS",
                "startIndex": total_r - 1, "endIndex": total_r},
                "inheritFromBefore": True}}]}).execute()
        r = total_r

        def pick(label):
            return (f"=IFERROR(INDEX('{cur}'!E:E;"
                    f"MATCH(\"{label}\";'{cur}'!A:A;0));0)")
        sheets.spreadsheets().values().update(
            spreadsheetId=SID, range=f"'📊 Anual'!A{r}:F{r}",
            valueInputOption="USER_ENTERED",
            body={"values": [[cur, pick("TOTAL INGRESOS"), pick("TOTAL FIJOS"),
                              pick("TOTAL VARIABLE"), f"=C{r}+D{r}",
                              f"=B{r}-E{r}"]]}).execute()
        # extend TOTAL sums
        new_total = total_r + 1
        sheets.spreadsheets().values().update(
            spreadsheetId=SID, range=f"'📊 Anual'!B{new_total}:F{new_total}",
            valueInputOption="USER_ENTERED",
            body={"values": [[f"=SUM({c}3:{c}{r})" for c in "BCDEF"]]}).execute()
        print(f"Anual: fila '{cur}' agregada.")

    # Net worth snapshot
    nw = sheets.spreadsheets().values().get(
        spreadsheetId=SID, range="'💰📊 Cash + Big Buys'!E24:E29",
        valueRenderOption="UNFORMATTED_VALUE").execute().get("values", [])
    sheets.spreadsheets().values().append(
        spreadsheetId=SID, range="'📈 Net Worth'!A2",
        valueInputOption="USER_ENTERED",
        body={"values": [[today.isoformat(), round(nw[0][0], 2),
                          round(nw[2][0], 2), round(nw[5][0], 2)]]}).execute()
    print("Net worth snapshot guardado.")

    # Hide the closed month's tab to keep the tab bar clean
    if prev in tabs:
        sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={"requests": [
            {"updateSheetProperties": {"properties": {
                "sheetId": tabs[prev]["sheetId"], "hidden": True},
                "fields": "hidden"}}]}).execute()
        print(f"Tab '{prev}' oculta.")

    # Summary draft for the closed month
    ing = get_total(sheets, prev, "TOTAL INGRESOS")
    fij = get_total(sheets, prev, "TOTAL FIJOS")
    var = get_total(sheets, prev, "TOTAL VARIABLE")
    bal = ing - fij - var
    gmail_draft(
        f"📊 Cierre {prev}: balance ${bal:,.0f}",
        f"Cierre de {prev}:\n\n"
        f"Ingresos:  ${ing:,.0f}\nFijos:     ${fij:,.0f}\n"
        f"Variables: ${var:,.0f}\nBalance:   ${bal:,.0f}\n\n"
        f"Net worth: ${nw[0][0]:,.0f} (neto sin inmuebles ${nw[5][0]:,.0f})\n"
        f"Pestaña {cur} creada y lista.\n"
        f"https://docs.google.com/spreadsheets/d/{SID}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--burn-check", action="store_true")
    args = p.parse_args()
    sheets, _ = get_services()
    if args.burn_check:
        burn_check(sheets)
    else:
        close_month(sheets)


if __name__ == "__main__":
    main()
