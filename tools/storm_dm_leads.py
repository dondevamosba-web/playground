#!/usr/bin/env python3
"""
CRM for Storm DM-audit responders (people who replied "AUDIT" to posts/DMs).

Usage:
  python3 tools/storm_dm_leads.py setup
  python3 tools/storm_dm_leads.py add @joes_roofing roofing --notes "respondió al post 34"
  python3 tools/storm_dm_leads.py touch @joes_roofing --notes "le mandé el audit" [--stage audit_sent]
  python3 tools/storm_dm_leads.py due            # follow-ups vencidos (>3 días sin contacto)
  python3 tools/storm_dm_leads.py list

Stages: new → audit_sent → call_booked → client | lost. Sheet ID in .env STORM_DM_LEADS_ID.
"""
import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from sheets_client import get_services

ENV_FILE = ROOT / ".env"
ENV_KEY = "STORM_DM_LEADS_ID"
TAB = "Leads"
HEADERS = ["Handle", "Vertical", "Stage", "Primer contacto", "Último contacto", "Notas"]
FOLLOWUP_DAYS = 3
ACTIVE = {"new", "audit_sent", "call_booked"}


def get_id():
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith(f"{ENV_KEY}="):
            return line.split("=", 1)[1].strip()
    return None


def rows(sheets, sid):
    res = sheets.spreadsheets().values().get(spreadsheetId=sid, range=f"{TAB}!A2:F").execute()
    return [r + [""] * (6 - len(r)) for r in res.get("values", [])]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    a1 = sub.add_parser("add"); a1.add_argument("handle"); a1.add_argument("vertical"); a1.add_argument("--notes", default="")
    a2 = sub.add_parser("touch"); a2.add_argument("handle"); a2.add_argument("--notes", default=""); a2.add_argument("--stage")
    sub.add_parser("due")
    sub.add_parser("list")
    a = ap.parse_args()

    sheets, _ = get_services()
    sid = get_id()

    if a.cmd == "setup":
        if sid:
            sys.exit(f"Ya existe: https://docs.google.com/spreadsheets/d/{sid}")
        ss = sheets.spreadsheets().create(body={
            "properties": {"title": "Storm — DM Leads"},
            "sheets": [{"properties": {"title": TAB}}]}).execute()
        sid = ss["spreadsheetId"]
        sheets.spreadsheets().values().update(spreadsheetId=sid, range=f"{TAB}!A1",
            valueInputOption="RAW", body={"values": [HEADERS]}).execute()
        with open(ENV_FILE, "a") as f:
            f.write(f"\n{ENV_KEY}={sid}\n")
        print(f"Created: https://docs.google.com/spreadsheets/d/{sid}")
        return

    if not sid:
        sys.exit("Corré primero: python3 tools/storm_dm_leads.py setup")
    data = rows(sheets, sid)

    if a.cmd == "add":
        today = str(date.today())
        sheets.spreadsheets().values().append(spreadsheetId=sid, range=f"{TAB}!A:F",
            valueInputOption="RAW",
            body={"values": [[a.handle, a.vertical, "new", today, today, a.notes]]}).execute()
        print(f"Agregado {a.handle} ({a.vertical})")
    elif a.cmd == "touch":
        for i, r in enumerate(data):
            if r[0].lstrip("@") == a.handle.lstrip("@"):
                r[4] = str(date.today())
                if a.stage:
                    r[2] = a.stage
                if a.notes:
                    r[5] = (r[5] + " | " if r[5] else "") + f"{date.today():%d/%m}: {a.notes}"
                sheets.spreadsheets().values().update(spreadsheetId=sid,
                    range=f"{TAB}!A{i + 2}:F{i + 2}", valueInputOption="RAW",
                    body={"values": [r]}).execute()
                print(f"Actualizado {r[0]} → stage {r[2]}")
                return
        sys.exit(f"{a.handle} no está en el sheet")
    elif a.cmd in ("due", "list"):
        cutoff = date.today() - timedelta(FOLLOWUP_DAYS)
        shown = 0
        for r in data:
            last = datetime.strptime(r[4], "%Y-%m-%d").date() if r[4] else None
            overdue = r[2] in ACTIVE and last and last <= cutoff
            if a.cmd == "due" and not overdue:
                continue
            flag = " ⚠ FOLLOW UP" if overdue else ""
            print(f"{r[0]:<22} {r[1]:<10} {r[2]:<12} último: {r[4]}{flag}  {r[5][:50]}")
            shown += 1
        if a.cmd == "due" and not shown:
            print("Nada vencido. 👌")


if __name__ == "__main__":
    main()
