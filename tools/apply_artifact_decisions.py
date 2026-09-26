#!/usr/bin/env python3
"""
Apply approve/reject decisions exported from the "Mesa de Posteos" artifact
to the Google Sheets the auto-posters read.

The artifact saves decisions in its own store and exports them as a JSON file
("Exportar decisiones"). Each decision says where its row lives:
  - source "approval": unified approval sheet, tab = account. Matched on
    Queued At + first 60 chars of the caption. Writes Status and Comments.
  - source "calendar": the account's content calendar (first sheet). Matched on
    Date + Time + first 60 chars of the caption. Writes Status.
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="JSON exported from the artifact")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    decisions = json.loads(Path(args.file).read_text(encoding="utf-8"))
    sheets, _ = get_services()
    updates = {}  # sheet_id -> list of range updates
    skipped = []

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
                upd = {"range": f"{st}{row_num}", "values": [[d["status"]]]}
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
    print(f"\n{n} fila(s) {'a actualizar (dry-run)' if args.dry_run else 'actualizadas'}, {len(skipped)} salteada(s).")


if __name__ == "__main__":
    main()
