#!/usr/bin/env python3
"""
Create (or reformat) the unified Instagram approval sheet with one tab per account.
Columns: Queued At | Caption | Image URL | Schedule Date | Status | Comments | Post ID
"""

import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

ACCOUNTS = ["Ola Digital", "Storm", "Fiestas", "Techno"]

HEADERS = [
    "Queued At", "Caption", "Image URL", "Schedule Date",
    "Status", "Comments", "Post ID"
]

STATUS_OPTIONS = ["draft", "approved", "rejected"]


def create_sheet(existing_id=None):
    sheets, _ = get_services()

    if existing_id:
        sheet_id = existing_id
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        result = sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
        print(f"Using existing sheet: {sheet_url}")
    else:
        body = {
            "properties": {"title": "Instagram Approval — All Accounts"},
            "sheets": [
                {"properties": {"title": acct, "index": i}}
                for i, acct in enumerate(ACCOUNTS)
            ]
        }
        result = sheets.spreadsheets().create(body=body).execute()
        sheet_id = result["spreadsheetId"]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        print(f"Created: {sheet_url}")

    tab_ids = {
        s["properties"]["title"]: s["properties"]["sheetId"]
        for s in result["sheets"]
    }

    requests = []

    for acct in ACCOUNTS:
        tid = tab_ids[acct]

        # Write headers
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{acct}'!A1",
            valueInputOption="RAW",
            body={"values": [HEADERS]}
        ).execute()

        requests += [
            # Bold + dark header row
            {
                "repeatCell": {
                    "range": {"sheetId": tid, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1}
                            },
                            "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2}
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            # Freeze header row
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": tid,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            },
            # Status dropdown (column E = index 4)
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": tid,
                        "startRowIndex": 1, "endRowIndex": 1000,
                        "startColumnIndex": 4, "endColumnIndex": 5
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": s} for s in STATUS_OPTIONS]
                        },
                        "showCustomUi": True,
                        "strict": True
                    }
                }
            },
            # Green for approved
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 1000}],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "approved"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 0.714, "green": 0.843, "blue": 0.659}
                            }
                        }
                    },
                    "index": 0
                }
            },
            # Red for rejected
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 1000}],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "rejected"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 0.918, "green": 0.600, "blue": 0.600}
                            }
                        }
                    },
                    "index": 1
                }
            },
            # Yellow for draft
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{"sheetId": tid, "startRowIndex": 1, "endRowIndex": 1000}],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": "draft"}]
                            },
                            "format": {
                                "backgroundColor": {"red": 1.0, "green": 0.949, "blue": 0.800}
                            }
                        }
                    },
                    "index": 2
                }
            },
            # Wider caption column (B = index 1)
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": tid, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},
                    "properties": {"pixelSize": 400},
                    "fields": "pixelSize"
                }
            },
            # Wider comments column (F = index 5)
            {
                "updateDimensionProperties": {
                    "range": {"sheetId": tid, "dimension": "COLUMNS", "startIndex": 5, "endIndex": 6},
                    "properties": {"pixelSize": 280},
                    "fields": "pixelSize"
                }
            },
        ]

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": requests}
    ).execute()

    print(f"\nDone. Sheet ID: {sheet_id}")
    print(f"URL: {sheet_url}")
    return sheet_id, sheet_url


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--existing-id", help="Apply formatting to an already-created sheet")
    args = p.parse_args()
    create_sheet(existing_id=args.existing_id)
