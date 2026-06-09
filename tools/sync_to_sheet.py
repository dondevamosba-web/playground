#!/usr/bin/env python3
"""
Push calendar approvals directly into the Google Sheets for Storm, Techno, and Fiestas.
Called by the calendar server when a post is approved/unapproved via drag-drop or panel.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services


# ── Storm ──────────────────────────────────────────────────────────────────────

def sync_storm(post: dict, unapprove: bool = False):
    """Upsert a Storm post row in the Storm content calendar sheet."""
    sheets, drive = get_services()
    sheet_id = os.getenv("STORM_CONTENT_CALENDAR_SHEET_ID")

    resp = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A:J"
    ).execute()
    rows = resp.get("values", [])

    date_val = post.get("date", "")
    time_val = post.get("time", "09:00") or "09:00"
    file_val = post.get("file", "")
    label    = post.get("label", "")
    caption  = post.get("caption", "")

    # derive day name
    try:
        day_name = datetime.strptime(date_val, "%Y-%m-%d").strftime("%A")
    except Exception:
        day_name = ""

    # Check if row already exists for this post (match by label in col 3)
    existing_idx = None
    for i, row in enumerate(rows[1:], start=2):  # 1-based sheet row
        if len(row) > 3 and row[3] == label:
            existing_idx = i
            break

    if unapprove:
        if existing_idx:
            sheets.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"I{existing_idx}",
                valueInputOption="RAW",
                body={"values": [["removed"]]},
            ).execute()
        return

    new_row = [
        date_val,
        time_val,
        day_name,
        label,
        "single",
        caption,
        "",   # hashtags — filled later
        file_val,
        "pending",
        "",   # post ID
    ]

    if existing_idx:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"A{existing_idx}:J{existing_idx}",
            valueInputOption="RAW",
            body={"values": [new_row]},
        ).execute()
        print(f"[sync_storm] Updated row {existing_idx}: {label} → {date_val} {time_val}")
    else:
        sheets.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A:J",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [new_row]},
        ).execute()
        print(f"[sync_storm] Appended: {label} → {date_val} {time_val}")


# ── Techno ─────────────────────────────────────────────────────────────────────

def sync_techno(post: dict, unapprove: bool = False):
    """Upsert a Techno post row in the Techno content calendar sheet."""
    sheets, _ = get_services()
    sheet_id = os.getenv("TECHNO_CONTENT_CALENDAR_SHEET_ID")

    resp = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A:K"
    ).execute()
    rows = resp.get("values", [])

    date_val  = post.get("schedule_date") or post.get("date", "")
    time_val  = post.get("time", "10:00") or "10:00"
    product   = post.get("product", "")
    brand     = post.get("brand", "")
    post_type = post.get("type", "offer")
    caption   = post.get("caption", "")
    image_url = post.get("image_url", "")

    try:
        day_name = datetime.strptime(date_val, "%Y-%m-%d").strftime("%A")
    except Exception:
        day_name = ""

    # Match by product name in col 3 (index 3)
    existing_idx = None
    for i, row in enumerate(rows[1:], start=2):
        if len(row) > 3 and row[3] == product:
            existing_idx = i
            break

    if unapprove:
        if existing_idx:
            sheets.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"J{existing_idx}",
                valueInputOption="RAW",
                body={"values": [["removed"]]},
            ).execute()
        return

    new_row = [
        date_val,
        time_val,
        day_name,
        product,
        brand,
        "offer",
        caption,
        "",       # hashtags
        image_url,
        "pending",
        "",       # post ID
    ]

    if existing_idx:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"A{existing_idx}:K{existing_idx}",
            valueInputOption="RAW",
            body={"values": [new_row]},
        ).execute()
        print(f"[sync_techno] Updated row {existing_idx}: {product} → {date_val} {time_val}")
    else:
        sheets.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A:K",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [new_row]},
        ).execute()
        print(f"[sync_techno] Appended: {product} → {date_val} {time_val}")


# ── Fiestas ────────────────────────────────────────────────────────────────────

def sync_fiestas(post: dict, unapprove: bool = False):
    """Set a Fiestas event row Status = 'approved' (or back to 'pending') in the sheet."""
    sheets, _ = get_services()
    sheet_id = os.getenv("FIESTAS_APPROVAL_SHEET_ID")

    resp = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Queue!A:N"
    ).execute()
    rows = resp.get("values", [])

    event_name = post.get("name", "")
    target_status = "pending" if unapprove else "approved"

    for i, row in enumerate(rows[1:], start=2):  # 1-based sheet row
        name_in_row = row[2] if len(row) > 2 else ""
        if name_in_row == event_name:
            sheets.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"Queue!L{i}",
                valueInputOption="RAW",
                body={"values": [[target_status]]},
            ).execute()
            print(f"[sync_fiestas] Row {i}: '{event_name[:40]}' → {target_status}")
            return

    print(f"[sync_fiestas] WARNING — event not found in sheet: {event_name[:50]}")


# ── Ola Digital ────────────────────────────────────────────────────────────────

def sync_ola(post: dict, unapprove: bool = False):
    """Update the Ola Digital sheet row status when approved/unapproved via calendar."""
    sheets, _ = get_services()
    sheet_id = os.getenv("CONTENT_CALENDAR_SHEET_ID")

    sheet_row = post.get("sheet_row")
    if not sheet_row:
        print(f"[sync_ola] No sheet_row in post, skipping")
        return

    new_status = "pending" if unapprove else "approved"
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"I{sheet_row}",
        valueInputOption="RAW",
        body={"values": [[new_status]]},
    ).execute()
    print(f"[sync_ola] Row {sheet_row}: {post.get('content_type','')[:40]} → {new_status}")


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def sync_post(project: str, post: dict, unapprove: bool = False):
    if project == "storm":
        sync_storm(post, unapprove)
    elif project == "techno":
        sync_techno(post, unapprove)
    elif project == "fiestas":
        sync_fiestas(post, unapprove)
    elif project == "ola":
        sync_ola(post, unapprove)
