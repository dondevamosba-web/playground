#!/usr/bin/env python3
"""Quick auth - get Google token and save it."""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
import json
import sys

ROOT = Path("/Users/guidocarminatti/Downloads/playground")

flow = InstalledAppFlow.from_client_secrets_file(
    str(ROOT / "credentials.json"),
    ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)

print("Opening browser for authorization...")
creds = flow.run_local_server(port=0)  # Use any available port

# Direct file save
token_file = ROOT / "token_sheets.json"
token_file.write_text(json.dumps({
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': creds.scopes,
    'type': 'authorized_user'
}, indent=2))

print(f"✓ Saved token to {token_file}")
if token_file.exists():
    print(f"✓ File verified: {token_file.stat().st_size} bytes")
else:
    print("✗ ERROR: File was not saved!")
    sys.exit(1)
