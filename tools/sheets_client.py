"""
Shared Google Sheets + Drive auth used by all outreach logging tools.
"""
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = ROOT / "credentials.json"
SERVICE_ACCOUNT_FILE = ROOT / "service_account.json"
TOKEN_FILE = ROOT / "token_sheets.json"


def get_services():
    creds = None
    
    # Try OAuth token first (works with Drive personal storage)
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"Failed to load OAuth token ({e})")
            creds = None
    
    # Fall back to service account if OAuth doesn't exist
    if not creds and SERVICE_ACCOUNT_FILE.exists():
        creds = ServiceAccountCredentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
        )
    
    # Last resort: generate new OAuth token
    if not creds:
        if CREDENTIALS_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            TOKEN_FILE.write_text(creds.to_json())
        else:
            print("ERROR: No service_account.json or credentials.json found in project root.")
            sys.exit(1)
    
    sheets = build("sheets", "v4", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return sheets, drive
