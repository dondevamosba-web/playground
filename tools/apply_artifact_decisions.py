#!/usr/bin/env python3
"""
Apply approve/reject decisions exported from the "Mesa de Posteos" artifact
to the Google Sheets the auto-posters read.

The artifact saves decisions in its own store and exports them as a JSON file
("Exportar decisiones"). Each decision says where its row lives:
  - source "approval": unified approval sheet, tab = account. Matched on
    Queued At + first 60 chars of the caption. Writes Status and Comments.
  - source "proposal": a new post proposed in the artifact. If approved, it is
    appended as a new row to the account's content calendar (status = what that
    autoposter publishes; Media URL left empty for you to fill). Rejected ones
    are not written. Skipped if a row with the same date, time and caption exists.
  - source "calendar": the account's content calendar (first sheet). Matched on
    Date + Time + first 60 chars of the caption. Writes Status; an approval is
    written as the status that account's autoposter publishes (Techno: "pending").
Rows already decided (approved/rejected/posted/skip) are left alone.

Usage:
  python3 tools/apply_artifact_decisions.py decisiones-posteos.json
  python3 tools/apply_artifact_decisions.py decisiones-posteos.json --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.posting_sources import (APPROVAL_SHEET_ID, APPROVAL_COLS, CALENDARS,
                                   OPEN_STATUSES, col_letter)


def read(sheets, sheet_id, rng):
    rows = sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=rng).execute().get("values", [])
    return [r + [""] * (26 - len(r)) for r in rows]


def append_proposals(sheets, proposals, dry_run):
    """Append approved proposals as new calendar rows. Returns how many were appended."""
    total = 0
    for account in sorted({d["account"] for d in proposals}):
        c = CALENDARS[account]
        existing = {(r[c["date"]], r[c["time"]], r[c["caption"]][:60]) for r in read(sheets, c["sheet_id"], "A1:Z2000")[1:]}
        new_rows = []
        for d in (d for d in proposals if d["account"] == account):
            if d["status"] != "approved":
                print(f"{account} (propuesta) {d['date']}: rechazada, no se agrega")
                continue
            if (d["date"], d["time"], d["caption"][:60]) in existing:
                print(f"SKIP {account} (propuesta) {d['date']}: ya está en el calendario")
                continue
            row = [""] * (max(v for k, v in c.items() if isinstance(v, int)) + 1)
            for field, value in [("date", d["date"]), ("time", d["time"]), ("day", d.get("day", "")),
                                 ("title", d.get("title", "")), ("brand", d.get("brand", "")), ("type", d.get("postType", "")),
                                 ("caption", d["caption"]), ("hashtags", d.get("hashtags", "")), ("status", c["publishes"])]:
                if field in c:
                    row[c[field]] = value
            new_rows.append(row)
            print(f"{account} (propuesta) {d['date']} {d['time']}: se agrega  {d['caption'][:40]}")
        if new_rows and not dry_run:
            sheets.spreadsheets().values().append(
                spreadsheetId=c["sheet_id"], range="A1", valueInputOption="RAW",
                insertDataOption="INSERT_ROWS", body={"values": new_rows}).execute()
        total += len(new_rows)
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="JSON exported from the artifact")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    decisions = json.loads(Path(args.file).read_text(encoding="utf-8"))
    sheets, _ = get_services()
    updates = {}  # sheet_id -> list of range updates
    skipped = []

    appended = append_proposals(sheets, [d for d in decisions if d["source"] == "proposal"], args.dry_run)
    decisions = [d for d in decisions if d["source"] != "proposal"]

    # Group by (sheet, tab) so each sheet is read once
    groups = {}
    for d in decisions:
        if d["source"] == "calendar":
            cfg = CALENDARS[d["account"]]
            groups.setdefault((cfg["sheet_id"], "", d["account"]), []).append(d)
        else:
            groups.setdefault((APPROVAL_SHEET_ID, d["account"], None), []).append(d)

    for (sheet_id, tab, cal_account), items in groups.items():
        prefix = f"'{tab}'!" if tab else ""
        rows = read(sheets, sheet_id, f"{prefix}A1:Z2000")
        c = CALENDARS[cal_account] if cal_account else APPROVAL_COLS
        index = {}
        for i, row in enumerate(rows[1:], start=2):
            key = (row[c["date"]], row[c["time"]]) if cal_account else (row[c["queued"]],)
            index[key + (row[c["caption"]][:60],)] = (i, row[c["status"]].strip().lower())

        for d in items:
            key = (d["date"], d["time"]) if cal_account else (d["queuedAt"],)
            hit = index.get(key + (d["captionStart"],))
            label = f"{d['account']} ({'calendario' if cal_account else 'aprobación'})"
            if not hit:
                skipped.append(f"{label}: no encontrada — {d['captionStart'][:40]}")
                continue
            row_num, current = hit
            if current not in OPEN_STATUSES:
                skipped.append(f"{label} fila {row_num}: ya estaba '{current}'")
                continue
            st = col_letter(c["status"])
            if cal_account:
                # Approving writes whatever status this account's autoposter publishes
                new = c["publishes"] if d["status"] == "approved" else d["status"]
                upd = {"range": f"{st}{row_num}", "values": [[new]]}
            else:
                upd = {"range": f"{prefix}{st}{row_num}:{col_letter(c['comment'])}{row_num}",
                       "values": [[d["status"], d.get("comment", "")]]}
            updates.setdefault(sheet_id, []).append(upd)
            print(f"{label} fila {row_num}: {d['status']}  {d['captionStart'][:40]}")

    for s in skipped:
        print(f"SKIP {s}")

    if not args.dry_run:
        for sheet_id, data in updates.items():
            sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id, body={"valueInputOption": "RAW", "data": data}
            ).execute()
    n = sum(len(v) for v in updates.values())
    print(f"\n{n} fila(s) {'a actualizar (dry-run)' if args.dry_run else 'actualizadas'}, "
          f"{appended} propuesta(s) {'a agregar' if args.dry_run else 'agregadas'}, {len(skipped)} salteada(s).")


if __name__ == "__main__":
    main()
