#!/usr/bin/env python3
"""Adds a Precios Apple tab to the organized spreadsheet."""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SS_ID = "1fUmZGaPuc8ro2MqTIu9ZrEeLh-lsgKa_U5b7aBdaTHY"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_creds():
    return Credentials.from_authorized_user_file(
        "/Users/guidocarminatti/Downloads/playground/token_sheets.json", SCOPES
    )

# ─── DATA ────────────────────────────────────────────────────────────────────
# (Categoría, Modelo, Storage, RAM, Precio USD, Notas)

APPLE_DATA = [
    # MacBook Air M1
    ("MacBook Air M1 13\"", "MacBook Air M1", "256 GB", "8 GB", 900, ""),
    ("MacBook Air M1 13\"", "MacBook Air M1", "512 GB", "8 GB", 1110, ""),
    ("MacBook Air M1 13\"", "MacBook Air M1", "256 GB", "16 GB", 1300, ""),
    ("MacBook Air M1 13\"", "MacBook Air M1", "512 GB", "16 GB", 1520, ""),

    # MacBook Pro M1 13"
    ("MacBook Pro M1 13\"", "MacBook Pro M1", "256 GB", "8 GB", 1230, ""),
    ("MacBook Pro M1 13\"", "MacBook Pro M1", "512 GB", "8 GB", 1340, ""),
    ("MacBook Pro M1 13\"", "MacBook Pro M1", "512 GB", "16 GB", 1850, ""),

    # MacBook Air M2 13"
    ("MacBook Air M2 13\"", "MacBook Air M2", "256 GB", "8 GB", 1250, ""),
    ("MacBook Air M2 13\"", "MacBook Air M2", "512 GB", "8 GB", 1570, ""),

    # MacBook Pro M2 13"
    ("MacBook Pro M2 13\"", "MacBook Pro M2", "256 GB", "8 GB", 1320, ""),
    ("MacBook Pro M2 13\"", "MacBook Pro M2", "512 GB", "8 GB", 1540, ""),
    ("MacBook Pro M2 13\"", "MacBook Pro M2", "1 TB", "16 GB", 2020, "Custom"),

    # MacBook Pro M1 14"
    ("MacBook Pro M1 14\"", "MacBook Pro M1 Pro", "512 GB", "16 GB", 1900, ""),
    ("MacBook Pro M1 14\"", "MacBook Pro M1 Pro", "1 TB", "16 GB", 2220, ""),
    ("MacBook Pro M1 14\"", "MacBook Pro M1 Pro", "512 GB", "32 GB", 2750, ""),
    ("MacBook Pro M1 14\"", "MacBook Pro M1 Pro", "1 TB", "32 GB", 3350, ""),

    # MacBook Pro M1 16"
    ("MacBook Pro M1 16\"", "MacBook Pro M1 Pro", "512 GB", "16 GB", 2320, ""),
    ("MacBook Pro M1 16\"", "MacBook Pro M1 Pro", "1 TB", "16 GB", 2540, ""),
    ("MacBook Pro M1 16\"", "MacBook Pro M1 Pro", "512 GB", "32 GB", 3050, ""),
    ("MacBook Pro M1 16\"", "MacBook Pro M1 Pro", "1 TB", "32 GB", 3550, ""),
    ("MacBook Pro M1 16\"", "MacBook Pro M1 Max", "1 TB", "32 GB", 3750, "M1 Max"),

    # MacBook Pro M2 Pro 14"
    ("MacBook Pro M2 14\"", "MacBook Pro M2 Pro", "512 GB", "16 GB", 2250, "10cpu 16gpu"),
    ("MacBook Pro M2 14\"", "MacBook Pro M2 Pro", "1 TB", "16 GB", 2800, "12cpu 19gpu"),

    # MacBook Pro M2 Pro Max 14" / 16"
    ("MacBook Pro M2 14\" Max", "MacBook Pro M2 Pro Max", "1 TB", "32 GB", 3480, "16cpu 30gpu"),
    ("MacBook Pro M2 16\" Max", "MacBook Pro M2 Pro Max", "1 TB", "32 GB", 4180, "12cpu 38gpu"),

    # iMac 24" M1
    ("iMac 24\" M1", "iMac M1", "256 GB", "8 GB", 1350, ""),
    ("iMac 24\" M1", "iMac M1 8C", "256 GB", "8 GB", 1620, "8-core GPU"),

    # iPhone 12
    ("iPhone 12 mini", "iPhone 12 mini", "64 GB", "-", 690, ""),
    ("iPhone 12 mini", "iPhone 12 mini", "128 GB", "-", 750, ""),
    ("iPhone 12 mini", "iPhone 12 mini", "256 GB", "-", 800, ""),
    ("iPhone 12", "iPhone 12", "64 GB", "-", 740, ""),
    ("iPhone 12", "iPhone 12", "128 GB", "-", 850, ""),
    ("iPhone 12 Pro", "iPhone 12 Pro", "256 GB", "-", 1100, ""),

    # iPhone 13
    ("iPhone 13 mini", "iPhone 13 mini", "128 GB", "-", 860, ""),
    ("iPhone 13 mini", "iPhone 13 mini", "256 GB", "-", 930, ""),
    ("iPhone 13", "iPhone 13", "128 GB", "-", 930, ""),
    ("iPhone 13", "iPhone 13", "256 GB", "-", 1030, ""),
    ("iPhone 13", "iPhone 13", "512 GB", "-", 1100, ""),
    ("iPhone 13 Pro", "iPhone 13 Pro", "128 GB", "-", 1160, ""),
    ("iPhone 13 Pro", "iPhone 13 Pro", "256 GB", "-", 1260, ""),
    ("iPhone 13 Pro", "iPhone 13 Pro", "512 GB", "-", 1500, ""),
    ("iPhone 13 Pro Max", "iPhone 13 Pro Max", "128 GB", "-", 1260, ""),
    ("iPhone 13 Pro Max", "iPhone 13 Pro Max", "256 GB", "-", 1360, ""),
    ("iPhone 13 Pro Max", "iPhone 13 Pro Max", "512 GB", "-", 1600, ""),
    ("iPhone 13 Pro Max", "iPhone 13 Pro Max", "1 TB", "-", 1820, ""),

    # iPhone 14
    ("iPhone 14", "iPhone 14", "128 GB", "-", 940, ""),
    ("iPhone 14", "iPhone 14", "256 GB", "-", 1040, ""),
    ("iPhone 14 Plus", "iPhone 14 Plus", "128 GB", "-", 1050, ""),
    ("iPhone 14 Plus", "iPhone 14 Plus", "256 GB", "-", 1160, ""),
    ("iPhone 14 Pro", "iPhone 14 Pro", "128 GB", "-", 1115, "sin SIM"),
    ("iPhone 14 Pro", "iPhone 14 Pro", "128 GB", "-", 1135, "con SIM"),
    ("iPhone 14 Pro", "iPhone 14 Pro", "256 GB", "-", 1230, "sin SIM"),
    ("iPhone 14 Pro", "iPhone 14 Pro", "256 GB", "-", 1250, "con SIM"),
    ("iPhone 14 Pro", "iPhone 14 Pro", "512 GB", "-", 1445, "sin SIM"),
    ("iPhone 14 Pro", "iPhone 14 Pro", "1 TB", "-", 1660, ""),
    ("iPhone 14 Pro Max", "iPhone 14 Pro Max", "128 GB", "-", 1220, "sin SIM"),
    ("iPhone 14 Pro Max", "iPhone 14 Pro Max", "256 GB", "-", 1320, "sin SIM"),
    ("iPhone 14 Pro Max", "iPhone 14 Pro Max", "512 GB", "-", 1560, "sin SIM"),
    ("iPhone 14 Pro Max", "iPhone 14 Pro Max", "1 TB", "-", 1770, ""),

    # iPad
    ("iPad 9na Gen", "iPad 9", "256 GB", "-", 465, ""),
    ("iPad Mini 6", "iPad Mini 6 (2021)", "256 GB", "-", 600, ""),
    ("iPad Air 5", "iPad Air 5", "64 GB", "-", 620, "Space/Blue/Pink/Purple"),
    ("iPad Pro 11\"", "iPad Pro 11\" M1", "128 GB", "-", 870, ""),
    ("iPad Pro 11\"", "iPad Pro 11\" M1", "256 GB", "-", 970, ""),
    ("iPad Pro 11\"", "iPad Pro 11\" M1", "512 GB", "-", 1100, ""),
    ("iPad Pro 12.9\"", "iPad Pro 12.9\" M1", "128 GB", "-", 1120, ""),
    ("iPad Pro 12.9\"", "iPad Pro 12.9\" M1", "256 GB", "-", 1260, ""),
    ("iPad Pro 12.9\"", "iPad Pro 12.9\" M1", "512 GB", "-", 1360, ""),

    # Apple Watch
    ("Apple Watch", "Series 3 38mm", "-", "-", 260, ""),
    ("Apple Watch", "SE 40mm", "-", "-", 330, ""),
    ("Apple Watch", "SE 44mm", "-", "-", 360, ""),
    ("Apple Watch", "Series 7 41mm", "-", "-", 380, ""),
    ("Apple Watch", "Series 7 45mm", "-", "-", 420, ""),
    ("Apple Watch", "Series 7 41mm + LTE", "-", "-", 560, ""),
    ("Apple Watch", "Series 7 45mm + LTE", "-", "-", 590, ""),
    ("Apple Watch", "Series 8 41mm", "-", "-", 510, ""),
    ("Apple Watch", "Series 8 45mm", "-", "-", 545, ""),

    # AirPods
    ("AirPods", "AirPods 2da Gen", "-", "-", 145, ""),
    ("AirPods", "AirPods 3ra Gen", "-", "-", 180, "MagSafe"),
    ("AirPods", "AirPods Pro", "-", "-", 200, "MagSafe"),
    ("AirPods", "AirPods Pro 2 (2022)", "-", "-", 265, ""),

    # Accesorios iPad
    ("Accesorios iPad", "Smart Keyboard 11\"", "-", "-", 250, ""),
    ("Accesorios iPad", "Smart Keyboard 12.9\"", "-", "-", 280, ""),
    ("Accesorios iPad", "Magic Keyboard 11\"", "-", "-", 370, ""),
    ("Accesorios iPad", "Magic Keyboard 12.9\"", "-", "-", 400, ""),
    ("Accesorios iPad", "Apple Pencil 1ra Gen", "-", "-", 120, ""),
    ("Accesorios iPad", "Apple Pencil 2da Gen", "-", "-", 140, ""),

    # Otros
    ("Otros", "Magic Mouse 2", "-", "-", 130, ""),
    ("Otros", "HomePod Mini", "-", "-", 170, ""),
    ("Otros", "PlayStation 5 (c/ lectora)", "825 GB", "-", 920, ""),
    ("Otros", "Joystick PS5 Wireless", "-", "-", 90, ""),
    ("Otros", "USB-C 20W (x1)", "-", "-", 25, ""),
    ("Otros", "USB-C 20W (x5)", "-", "-", 11, "por unidad"),
    ("Otros", "USB-C 20W (x10)", "-", "-", 9, "por unidad"),
    ("Otros", "USB-C 20W (x50)", "-", "-", 8, "por unidad"),

    # Xiaomi (Lucy)
    ("Xiaomi (Lucy)", "Redmi Note 11", "128 GB", "4 GB", 250, "Gray/Blue"),
    ("Xiaomi (Lucy)", "Redmi Note 11 Pro 5G", "128 GB", "6 GB", 350, "Blue/White"),
    ("Xiaomi (Lucy)", "POCO M4 Pro 5G", "128 GB", "6 GB", 280, "Black"),
]

TAB_COLOR = {"red": 0.8, "green": 0.8, "blue": 0.85}
HEADER_BG = {"red": 0.15, "green": 0.15, "blue": 0.2}
HEADER_FG = {"red": 0.7, "green": 0.85, "blue": 1.0}
ROW_EVEN = {"red": 0.1, "green": 0.1, "blue": 0.12}
ROW_ODD  = {"red": 0.07, "green": 0.07, "blue": 0.09}
TEXT_FG  = {"red": 0.9, "green": 0.9, "blue": 0.9}
CAT_BG   = {"red": 0.18, "green": 0.18, "blue": 0.25}
CAT_FG   = {"red": 0.7, "green": 0.85, "blue": 1.0}

HEADER = ["Categoría", "Modelo", "Storage", "RAM", "Precio USD", "Notas"]


def main():
    creds = get_creds()
    service = build("sheets", "v4", credentials=creds)

    # Add new sheet
    add_sheet = service.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID,
        body={"requests": [{"addSheet": {"properties": {"title": "Precios Apple"}}}]}
    ).execute()
    sheet_id = add_sheet["replies"][0]["addSheet"]["properties"]["sheetId"]

    # Build rows with category group rows
    rows = []
    current_cat = None
    for row in APPLE_DATA:
        cat = row[0]
        if cat != current_cat:
            current_cat = cat
            rows.append(("__CAT__", cat))
        rows.append(row)

    cell_rows = []
    for row_idx, row in enumerate([tuple(HEADER)] + rows):
        if row[0] == "__CAT__":
            # Category separator row
            cell_rows.append({
                "values": [
                    {
                        "userEnteredValue": {"stringValue": row[1] if i == 0 else ""},
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "foregroundColor": CAT_FG, "fontSize": 10},
                            "backgroundColor": CAT_BG,
                            "verticalAlignment": "MIDDLE",
                        }
                    }
                    for i in range(len(HEADER))
                ]
            })
        elif row_idx == 0:
            # Header
            cell_rows.append({
                "values": [
                    {
                        "userEnteredValue": {"stringValue": str(cell)},
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "foregroundColor": HEADER_FG},
                            "backgroundColor": HEADER_BG,
                            "verticalAlignment": "MIDDLE",
                        }
                    }
                    for cell in row
                ]
            })
        else:
            bg = ROW_EVEN if row_idx % 2 == 0 else ROW_ODD
            values = []
            for i, cell in enumerate(row):
                val = str(cell) if cell != "-" else ""
                entry = {
                    "userEnteredValue": {"stringValue": val} if i != 4 else {"numberValue": cell},
                    "userEnteredFormat": {
                        "textFormat": {"foregroundColor": TEXT_FG},
                        "backgroundColor": bg,
                        "verticalAlignment": "MIDDLE",
                        "horizontalAlignment": "RIGHT" if i == 4 else "LEFT",
                    }
                }
                values.append(entry)
            cell_rows.append({"values": values})

    requests = [
        # Tab color
        {"updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "tabColorStyle": {"rgbColor": TAB_COLOR}},
            "fields": "tabColorStyle"
        }},
        # Freeze header
        {"updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount"
        }},
        # Data
        {"updateCells": {
            "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
            "rows": cell_rows,
            "fields": "userEnteredValue,userEnteredFormat"
        }},
        # Auto-resize
        {"autoResizeDimensions": {
            "dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": len(HEADER)}
        }},
        # Format precio column as currency
        {"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "startColumnIndex": 4, "endColumnIndex": 5},
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {"type": "NUMBER", "pattern": '"$"#,##0'},
                    "horizontalAlignment": "RIGHT",
                }
            },
            "fields": "userEnteredFormat.numberFormat,userEnteredFormat.horizontalAlignment"
        }},
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=SS_ID, body={"requests": requests}
    ).execute()

    print(f"Done! https://docs.google.com/spreadsheets/d/{SS_ID}")


if __name__ == "__main__":
    main()
