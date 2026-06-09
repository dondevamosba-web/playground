#!/usr/bin/env python3
"""
One-shot script:
  1. Upload june + july singles to Google Drive
  2. Add 8 hourly rows to the content calendar for today (12:00–19:00)
  3. Fill media URLs on existing june/july calendar rows (7–21)

Run: python3 tools/setup_today_blitz.py
"""
import json, os, sys, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

from tools.sheets_client import get_services
from googleapiclient.http import MediaFileUpload

AR_TZ = timezone(timedelta(hours=-3))
TODAY = datetime.now(tz=AR_TZ).strftime('%Y-%m-%d')
SHEET_ID = os.getenv('CONTENT_CALENDAR_SHEET_ID')
DRIVE_FOLDER = 'Ola Digital/Junio-Julio 2026'

HASHTAGS = (
    '#OlaDigital #OlaDigitalOlavarría #Olavarría #OlavarríaBsAs '
    '#PymesOlavarría #NegociosOlavarría #MarketingDigital #MarketingArgentina '
    '#AgenciaDigital #RedesSociales #SEOLocal #GoogleAds #Emprendedores #PymeArgentina'
)

# ── Files to upload ───────────────────────────────────────────────────────────
ASSETS = ROOT / 'brand-toolkit' / 'ola-digital-assets'

JUNE_SINGLES = {
    'PostA': ASSETS / '08-junio-singles' / 'jun-A-de-2-a-15-reservas.png',
    'PostB': ASSETS / '08-junio-singles' / 'jun-B-google-my-business.png',
    'PostC': ASSETS / '08-junio-singles' / 'jun-C-dato-89.png',
    'PostD': ASSETS / '08-junio-singles' / 'jun-D-reels-publico.png',
    'PostE': ASSETS / '08-junio-singles' / 'jun-E-perfil-vidriera.png',
    'PostF': ASSETS / '08-junio-singles' / 'jun-F-dato-87.png',
    'PostG': ASSETS / '08-junio-singles' / 'jun-G-cero-a-agenda.png',
    'PostH': ASSETS / '08-junio-singles' / 'jun-H-consistencia.png',
    'PostI': ASSETS / '08-junio-singles' / 'jun-I-cierre-dramatico.png',
}
JULY_SINGLES = {
    'PostJ': ASSETS / '10-julio-singles' / 'jul-J-sin-google-maps.png',
    'PostK': ASSETS / '10-julio-singles' / 'jul-K-73pct-reviews.png',
    'PostL': ASSETS / '10-julio-singles' / 'jul-L-respuesta-30s.png',
    'PostM': ASSETS / '10-julio-singles' / 'jul-M-instagram-nunca-cierra.png',
    'PostN': ASSETS / '10-julio-singles' / 'jul-N-caso-estudio-contable.png',
    'PostO': ASSETS / '10-julio-singles' / 'jul-O-3-cosas-bio.png',
    'PostP': ASSETS / '10-julio-singles' / 'jul-P-si-no-en-google.png',
    'PostQ': ASSETS / '10-julio-singles' / 'jul-Q-5-segundos.png',
    'PostR': ASSETS / '10-julio-singles' / 'jul-R-web-lenta-vs-rapida.png',
    'PostS': ASSETS / '10-julio-singles' / 'jul-S-que-se-vea.png',
}
JUNE_CAROUSEL_COVERS = {
    'C1': ASSETS / '09-junio-carruseles' / 'jun-C1-1-cover.png',
    'C2': ASSETS / '09-junio-carruseles' / 'jun-C2-1-cover.png',
    'C3': ASSETS / '09-junio-carruseles' / 'jun-C3-1-cover.png',
    'C4': ASSETS / '09-junio-carruseles' / 'jun-C4-1-cover.png',
    'C5': ASSETS / '09-junio-carruseles' / 'jun-C5-1-cover.png',
    'C6': ASSETS / '09-junio-carruseles' / 'jun-C6-1-cover.png',
}

# ── Captions for today's new rows ─────────────────────────────────────────────
TODAY_ROWS = [
    # [date, time, day, content_type, post_type, caption, hashtags, media_key, status]
    [TODAY, '12:00', 'Wednesday', 'Caso real: de 2 a 15 reservas', 'single',
     'Un restaurante en Olavarría tenía 2 consultas por mes por redes. A los 30 días: 15 reservas semanales.\n\n¿Qué cambió? No el menú. La presencia digital.\n\nGoogle Maps optimizado + Instagram activo + respuestas rápidas = agenda llena.\n\n¿Tu negocio tiene el mismo problema? Escribinos.',
     HASHTAGS, 'PostA'],
    [TODAY, '13:00', 'Wednesday', 'Google My Business en 20 minutos', 'single',
     'Google My Business es gratis y lleva 20 minutos configurarlo bien.\n\n8 de cada 10 pymes en Olavarría no lo tienen optimizado. Eso les cuesta clientes todos los días.\n\nFoto, horarios, fotos del local, responder reseñas. Eso es todo.\n\n¿Querés que lo configuremos por vos? Escribinos al DM.',
     HASHTAGS, 'PostB'],
    [TODAY, '19:00', 'Wednesday', 'El 89% de las búsquedas locales', 'single',
     'El 89% de las búsquedas locales que no ven tu negocio se van con la competencia.\n\nNo es teoría. Pasa en Olavarría todos los días.\n\nLa gente busca "dentista cerca", "pizzería abierta ahora", "plomero de guardia". Si no aparecés, ya saben dónde van.\n\nAparecer no es magia. Es estrategia. Escribinos.',
     HASHTAGS, 'PostC'],
]

# ── Mapping of existing sheet rows (2-indexed from data row 1) to media keys ──
# Row index 0 = sheet row 2 (data row 1)
ROW_MEDIA_MAP = {
    # rows 6..14 (sheet rows 8-16, 0-indexed rows 6-14)
    6:  ('PostA', '2026-06-04', '12:00', 'single'),  # "De 2 consultas"
    8:  ('PostB', '2026-06-08', '08:00', 'single'),  # "Google My Business"
    9:  ('PostC', '2026-06-09', '12:00', 'single'),  # "89% búsquedas"
    11: ('PostD', '2026-06-11', '12:00', 'single'),  # "Los reels funcionan"
    13: ('PostE', '2026-06-15', '08:00', 'single'),  # "perfil vidriera"
    14: ('PostF', '2026-06-16', '12:00', 'single'),  # "competidor instagram"
    16: ('PostG', '2026-06-18', '12:00', 'single'),  # "ya ganando clientes"
    18: ('PostH', '2026-06-22', '08:00', 'single'),  # "consistencia"
    19: ('PostI', '2026-06-23', '12:00', 'single'),  # "cada cliente"
    # carousel rows → use cover slides
    5:  ('C1',    '2026-06-03', '19:00', 'single'),  # june C1 cover
    7:  ('C2',    '2026-06-05', '19:00', 'single'),  # june C2 cover
    10: ('C3',    '2026-06-10', '19:00', 'single'),  # june C3 cover
    12: ('C4',    '2026-06-12', '19:00', 'single'),  # june C4 cover
    15: ('C5',    '2026-06-17', '19:00', 'single'),  # june C5 cover
    17: ('C6',    '2026-06-19', '19:00', 'single'),  # june C6 cover
}


def get_or_create_folder(drive, folder_path):
    parts = [p for p in folder_path.strip('/').split('/') if p]
    parent_id = 'root'
    for part in parts:
        q = (f"name='{part}' and mimeType='application/vnd.google-apps.folder' "
             f"and '{parent_id}' in parents and trashed=false")
        res = drive.files().list(q=q, fields='files(id)').execute()
        files = res.get('files', [])
        if files:
            parent_id = files[0]['id']
        else:
            meta = {'name': part, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            f = drive.files().create(body=meta, fields='id').execute()
            parent_id = f['id']
            print(f'  Created folder: {part}')
    return parent_id


def upload_file(drive, path, folder_id):
    print(f'  Uploading {path.name}...', end=' ', flush=True)
    meta = {'name': path.name, 'parents': [folder_id]}
    media = MediaFileUpload(str(path), mimetype='image/png', resumable=True)
    f = drive.files().create(body=meta, media_body=media, fields='id,name').execute()
    drive.permissions().create(fileId=f['id'], body={'type': 'anyone', 'role': 'reader'}).execute()
    url = f'https://drive.google.com/uc?export=download&id={f["id"]}'
    print(f'OK  {url}')
    return url


def main():
    sheets, drive = get_services()

    # ── 1. Upload all files ──────────────────────────────────────────────────
    print(f'\n=== Uploading to Drive: {DRIVE_FOLDER} ===')
    folder_id = get_or_create_folder(drive, DRIVE_FOLDER)

    urls = {}
    all_files = {**JUNE_SINGLES, **JULY_SINGLES, **JUNE_CAROUSEL_COVERS}
    for key, path in all_files.items():
        if not path.exists():
            print(f'  SKIP {key} — file not found: {path}')
            continue
        urls[key] = upload_file(drive, path, folder_id)

    # Save URLs for reference
    url_cache = ROOT / '.tmp' / 'june_july_urls.json'
    url_cache.parent.mkdir(exist_ok=True)
    url_cache.write_text(json.dumps(urls, indent=2))
    print(f'\nURLs saved to {url_cache}')

    # ── 2. Read current sheet ────────────────────────────────────────────────
    print('\n=== Updating sheet ===')
    res = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range='A2:J1000'
    ).execute()
    rows = res.get('values', [])

    # ── 3. Update rows 0-4 (feed_04-08) to today with hourly slots ──────────
    today_feed_times = ['14:00', '15:00', '16:00', '17:00', '18:00']
    batch_updates = []

    for i, t in enumerate(today_feed_times):
        if i >= len(rows):
            break
        r = rows[i]
        # pad row to 10 cols
        while len(r) < 10:
            r.append('')
        r[0] = TODAY          # date → today
        r[1] = t              # time → hourly slot
        r[2] = 'Wednesday'
        batch_updates.append({
            'range': f'A{i+2}:J{i+2}',
            'values': [r[:10]],
        })
        print(f'  Row {i+2}: feed post → {TODAY} {t}')

    # ── 4. Fill media URLs on existing rows 5-19 (0-indexed) ────────────────
    for row_idx, (media_key, new_date, new_time, new_type) in ROW_MEDIA_MAP.items():
        if row_idx >= len(rows):
            continue
        r = rows[row_idx]
        while len(r) < 10:
            r.append('')
        r[0] = new_date
        r[1] = new_time
        r[4] = new_type
        r[7] = urls.get(media_key, r[7])  # media URL
        batch_updates.append({
            'range': f'A{row_idx+2}:J{row_idx+2}',
            'values': [r[:10]],
        })
        print(f'  Row {row_idx+2}: {new_date} {new_time} → {media_key}')

    # ── 5. Append today's new rows (jun-A 12:00, jun-B 13:00, jun-C 19:00) ──
    new_rows = []
    for r in TODAY_ROWS:
        media_key = r[7]
        row_data = r[:7] + [urls.get(media_key, ''), 'pending', '']
        new_rows.append(row_data)
        print(f'  Appending: {r[0]} {r[1]} → {media_key}')

    # Batch update existing rows
    if batch_updates:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={'valueInputOption': 'RAW', 'data': batch_updates},
        ).execute()
        print(f'  {len(batch_updates)} rows updated.')

    # Append new rows
    if new_rows:
        sheets.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range='A2',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': new_rows},
        ).execute()
        print(f'  {len(new_rows)} new rows appended.')

    print('\nDone! Sheet is ready.')
    print(f'\nToday\'s schedule ({TODAY}):')
    print('  12:00 → jun-A  (De 2 a 15 reservas)')
    print('  13:00 → jun-B  (Google My Business)')
    print('  14:00 → feed_04 (Sin web / clientes perdidos)')
    print('  15:00 → feed_05 (Google Ads)')
    print('  16:00 → feed_06 (Instagram competencia)')
    print('  17:00 → feed_07 (Email marketing)')
    print('  18:00 → feed_08 (Reputación online)')
    print('  19:00 → jun-C  (89% búsquedas locales)')


if __name__ == '__main__':
    main()
