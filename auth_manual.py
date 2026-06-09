#!/usr/bin/env python3
"""
Manual OAuth authorization for Google Sheets using local server.
"""
import os
import json
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).parent.parent if Path(__file__).parent.name == 'playground' else Path(__file__).parent
creds_file = (ROOT / 'credentials.json')
if not creds_file.exists():
    creds_file = Path.cwd() / 'credentials.json'
if not creds_file.exists():
    print("ERROR: credentials.json not found")
    sys.exit(1)

os.chdir(ROOT)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

print("\n" + "="*90)
print("GOOGLE AUTHORIZATION")
print("="*90)
print("\nStarting local server for OAuth callback...")
print("Your browser will open automatically. If not, visit the URL shown.\n")

try:
    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=True)
    
    # Save token
    token_path = ROOT / 'token_sheets.json'
    token_path.write_text(json.dumps({
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': SCOPES,
        'type': 'authorized_user'
    }, indent=2))
    
    print(f"\n✓ Token saved to {token_path.name}")
    print("✓ You can now run the posting command!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    sys.exit(1)
