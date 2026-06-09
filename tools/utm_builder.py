#!/usr/bin/env python3
"""
UTM builder + attribution logger.

Generates UTM-tagged URLs following a consistent naming convention,
logs them to a "UTM Tracker" Google Sheet, and reconciles against
Meta Ads spend/conversion data to surface discrepancies.

Sheet: "UTM Tracker"
Columns: Date | Base URL | Source | Medium | Campaign | Content | Term |
         Full UTM URL | Status | Meta Spend | Meta Conv | Manual Conv | Notes

Commands:
  build   — generate a UTM URL and log it to the sheet
  list    — show all logged UTMs (filter by campaign or source)
  log     — manually log conversion results against an existing UTM row
  reconcile — pull Meta Ads data and compare against sheet entries

Usage:
  python3 tools/utm_builder.py build \\
      --url "https://acme.com/roofing" \\
      --source facebook --medium paid_social \\
      --campaign "roofing_storm_q2_2026" \\
      --content "video_hook_a" --notes "Storm Digital client - Austin TX"

  python3 tools/utm_builder.py list
  python3 tools/utm_builder.py list --campaign roofing_storm_q2_2026
  python3 tools/utm_builder.py list --source facebook

  python3 tools/utm_builder.py log --campaign "roofing_storm_q2_2026" --conv 12 --notes "week 1 results"

  python3 tools/utm_builder.py reconcile           # compare sheet vs Meta Ads (requires META_ACCESS_TOKEN)
"""
import argparse
import os
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, urlencode

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_NAME = "UTM Tracker"
HEADERS = [
    "Date", "Base URL", "Source", "Medium", "Campaign",
    "Content", "Term", "Full UTM URL", "Status",
    "Meta Spend", "Meta Conv", "Manual Conv", "Notes",
]
# 0-based column indices
COL_DATE     = 0
COL_BASE_URL = 1
COL_SOURCE   = 2
COL_MEDIUM   = 3
COL_CAMPAIGN = 4
COL_CONTENT  = 5
COL_TERM     = 6
COL_FULL_URL = 7
COL_STATUS   = 8
COL_META_SPEND = 9
COL_META_CONV  = 10
COL_MANUAL_CONV = 11
COL_NOTES    = 12

GRAPH_URL = "https://graph.facebook.com/v19.0"


# ── Sheet helpers ─────────────────────────────────────────────────────────────

def _get_sheet_id(drive, sheets):
    q = f"name='{SHEET_NAME}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    files = drive.files().list(q=q, fields="files(id)").execute().get("files", [])
    if files:
        return files[0]["id"]

    # Create fresh
    sid = sheets.spreadsheets().create(
        body={"properties": {"title": SHEET_NAME}}, fields="spreadsheetId"
    ).execute()["spreadsheetId"]
    drive.permissions().create(
        fileId=sid, body={"type": "anyone", "role": "writer"}
    ).execute()
    _append(sheets, sid, [HEADERS])
    _bold_freeze(sheets, sid)
    print(f"Created sheet: {SHEET_NAME}")
    return sid


def _append(sheets, sid, rows):
    sheets.spreadsheets().values().append(
        spreadsheetId=sid, range="Sheet1!A1",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def _read_all(sheets, sid):
    result = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Sheet1!A:M"
    ).execute()
    return result.get("values", [])


def _update_row(sheets, sid, row_index: int, col: int, value: str):
    """Update a single cell (1-based row_index)."""
    col_letter = chr(ord("A") + col)
    sheets.spreadsheets().values().update(
        spreadsheetId=sid,
        range=f"Sheet1!{col_letter}{row_index}",
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]},
    ).execute()


def _bold_freeze(sheets, sid):
    meta = sheets.spreadsheets().get(spreadsheetId=sid).execute()
    grid_id = meta["sheets"][0]["properties"]["sheetId"]
    sheets.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": [
        {"repeatCell": {
            "range": {"sheetId": grid_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold",
        }},
        {"updateSheetProperties": {
            "properties": {"sheetId": grid_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }},
    ]}).execute()


def sheet_url(sid):
    return f"https://docs.google.com/spreadsheets/d/{sid}/edit"


# ── UTM generation ────────────────────────────────────────────────────────────

def build_utm_url(base_url: str, source: str, medium: str, campaign: str,
                  content: str = "", term: str = "") -> str:
    params = {
        "utm_source":   source.lower().replace(" ", "_"),
        "utm_medium":   medium.lower().replace(" ", "_"),
        "utm_campaign": campaign.lower().replace(" ", "_"),
    }
    if content:
        params["utm_content"] = content.lower().replace(" ", "_")
    if term:
        params["utm_term"] = term.lower().replace(" ", "_")

    # Preserve any existing query params on the base URL
    parsed = urlparse(base_url)
    existing = parse_qs(parsed.query)
    # UTM params take precedence
    merged = {k: v[0] for k, v in existing.items()}
    merged.update(params)
    new_query = urlencode(merged)
    return urlunparse(parsed._replace(query=new_query))


# ── Meta reconciliation ───────────────────────────────────────────────────────

def fetch_meta_by_campaign(token: str, account_ids: list,
                           date_start: str, date_end: str) -> dict:
    """Return {campaign_name_lower: {spend, conv}} for the given date range."""
    CONVERSION_ACTIONS = [
        "purchase", "offsite_conversion.fb_pixel_purchase",
        "lead",     "offsite_conversion.fb_pixel_lead",
    ]
    result = {}
    for account_id in account_ids:
        params = {
            "level": "campaign",
            "fields": "campaign_name,spend,actions",
            "time_range": f'{{"since":"{date_start}","until":"{date_end}"}}',
            "limit": 200,
            "access_token": token,
        }
        url = f"{GRAPH_URL}/{account_id}/insights"
        while url:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            for row in data.get("data", []):
                name = row.get("campaign_name", "").lower().replace(" ", "_")
                spend = float(row.get("spend", 0))
                actions = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
                conv = next((actions[k] for k in CONVERSION_ACTIONS if k in actions), 0.0)
                if name in result:
                    result[name]["spend"] += spend
                    result[name]["conv"]  += conv
                else:
                    result[name] = {"spend": spend, "conv": conv}
            url = data.get("paging", {}).get("next")
            params = {}
    return result


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_build(args, sheets, drive, sid):
    utm_url = build_utm_url(
        args.url, args.source, args.medium, args.campaign,
        getattr(args, "content", "") or "",
        getattr(args, "term", "") or "",
    )
    row = [
        date.today().isoformat(),
        args.url,
        args.source,
        args.medium,
        args.campaign,
        getattr(args, "content", "") or "",
        getattr(args, "term", "") or "",
        utm_url,
        "Active",
        "", "", "",  # Meta Spend, Meta Conv, Manual Conv
        getattr(args, "notes", "") or "",
    ]
    _append(sheets, sid, [row])
    print(f"\nUTM URL:\n  {utm_url}")
    print(f"\nLogged to sheet: {sheet_url(sid)}")


def cmd_list(args, sheets, sid):
    rows = _read_all(sheets, sid)
    if len(rows) <= 1:
        print("No UTMs logged yet. Use `build` to create one.")
        return

    filter_campaign = getattr(args, "campaign", None)
    filter_source   = getattr(args, "source", None)

    def get(row, col):
        return row[col].strip() if len(row) > col else ""

    data = rows[1:]
    if filter_campaign:
        data = [r for r in data if filter_campaign.lower() in get(r, COL_CAMPAIGN).lower()]
    if filter_source:
        data = [r for r in data if filter_source.lower() in get(r, COL_SOURCE).lower()]

    print(f"\n{'Date':<12} {'Campaign':<35} {'Source':<14} {'Medium':<14} {'M.Spend':>9} {'M.Conv':>7} {'Man.Conv':>9}")
    print("-" * 105)
    for r in data:
        print(
            f"{get(r, COL_DATE):<12} {get(r, COL_CAMPAIGN)[:33]:<35} "
            f"{get(r, COL_SOURCE):<14} {get(r, COL_MEDIUM):<14} "
            f"{get(r, COL_META_SPEND):>9} {get(r, COL_META_CONV):>7} {get(r, COL_MANUAL_CONV):>9}"
        )
    print(f"\n{len(data)} UTM(s) shown  ·  Sheet: {sheet_url(sid)}")


def cmd_log(args, sheets, sid):
    rows = _read_all(sheets, sid)
    campaign = args.campaign.lower()
    match_rows = [
        (i + 2, r) for i, r in enumerate(rows[1:])
        if campaign in (r[COL_CAMPAIGN].lower() if len(r) > COL_CAMPAIGN else "")
    ]
    if not match_rows:
        print(f"No UTM found for campaign '{args.campaign}'. Use `list` to see what's logged.")
        return

    # Update most recent match
    row_index, _ = match_rows[-1]
    if args.conv is not None:
        _update_row(sheets, sid, row_index, COL_MANUAL_CONV, str(args.conv))
    if args.notes:
        existing_notes = match_rows[-1][1][COL_NOTES] if len(match_rows[-1][1]) > COL_NOTES else ""
        new_notes = f"{existing_notes}; {args.notes}".lstrip("; ")
        _update_row(sheets, sid, row_index, COL_NOTES, new_notes)

    print(f"Updated row {row_index}: campaign='{args.campaign}', conv={args.conv}")
    print(f"Sheet: {sheet_url(sid)}")


def cmd_reconcile(args, sheets, sid):
    token = os.getenv("META_ACCESS_TOKEN")
    account_ids_raw = os.getenv("META_AD_ACCOUNT_ID", "")
    if not token or not account_ids_raw:
        print("META_ACCESS_TOKEN and META_AD_ACCOUNT_ID required in .env for reconciliation.")
        return

    account_ids = [a.strip() for a in account_ids_raw.split(",") if a.strip()]
    rows = _read_all(sheets, sid)
    if len(rows) <= 1:
        print("No UTMs in sheet to reconcile against.")
        return

    # Date range: last 30 days
    from datetime import timedelta
    date_end   = (date.today() - timedelta(days=1)).isoformat()
    date_start = (date.today() - timedelta(days=30)).isoformat()

    print(f"Fetching Meta data ({date_start} → {date_end})...")
    meta = fetch_meta_by_campaign(token, account_ids, date_start, date_end)

    print(f"\n{'Campaign':<35} {'UTM Source':<14} {'M.Spend':>9} {'M.Conv':>8} {'Man.Conv':>9} {'Gap':>8}")
    print("-" * 90)

    updated = 0
    for i, row in enumerate(rows[1:], start=2):
        def get(col):
            return row[col].strip() if len(row) > col else ""

        campaign_key = get(COL_CAMPAIGN).lower()
        meta_data = meta.get(campaign_key, {})
        spend = meta_data.get("spend", 0)
        conv  = meta_data.get("conv",  0)
        manual = get(COL_MANUAL_CONV)
        gap = ""
        if manual and conv:
            try:
                diff = float(manual) - conv
                gap = f"+{diff:.0f}" if diff > 0 else f"{diff:.0f}"
            except ValueError:
                pass

        if spend or conv:
            _update_row(sheets, sid, i, COL_META_SPEND, f"{spend:.2f}")
            _update_row(sheets, sid, i, COL_META_CONV,  f"{conv:.0f}")
            updated += 1

        print(
            f"{get(COL_CAMPAIGN)[:33]:<35} {get(COL_SOURCE):<14} "
            f"${spend:>8.2f} {conv:>8.0f} {manual:>9} {gap:>8}"
        )

    print(f"\n{updated} row(s) updated with Meta data.  Sheet: {sheet_url(sid)}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="utm_builder")
    sub = parser.add_subparsers(dest="cmd")

    # build
    p_build = sub.add_parser("build", help="Generate and log a UTM URL")
    p_build.add_argument("--url",      required=True)
    p_build.add_argument("--source",   required=True, help="e.g. facebook, google, email")
    p_build.add_argument("--medium",   required=True, help="e.g. paid_social, cpc, newsletter")
    p_build.add_argument("--campaign", required=True, help="e.g. roofing_storm_q2_2026")
    p_build.add_argument("--content",  default="",    help="e.g. video_hook_a")
    p_build.add_argument("--term",     default="",    help="e.g. roofing+contractor")
    p_build.add_argument("--notes",    default="")

    # list
    p_list = sub.add_parser("list", help="Show logged UTMs")
    p_list.add_argument("--campaign", default=None)
    p_list.add_argument("--source",   default=None)

    # log
    p_log = sub.add_parser("log", help="Log manual conversion results")
    p_log.add_argument("--campaign", required=True)
    p_log.add_argument("--conv",     type=float, default=None)
    p_log.add_argument("--notes",    default="")

    # reconcile
    sub.add_parser("reconcile", help="Pull Meta data and update sheet")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    sheets, drive = get_services()
    sid = _get_sheet_id(drive, sheets)

    if args.cmd == "build":
        cmd_build(args, sheets, drive, sid)
    elif args.cmd == "list":
        cmd_list(args, sheets, sid)
    elif args.cmd == "log":
        cmd_log(args, sheets, sid)
    elif args.cmd == "reconcile":
        cmd_reconcile(args, sheets, sid)


if __name__ == "__main__":
    main()
