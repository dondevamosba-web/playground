"""Authorize a Gmail account and save its token as token_gmail_<user>.json.

Usage: python3 tools/gmail_auth_account.py
Opens a browser; pick the account you want to authorize. Token is saved
named after the actual account that completed the flow.
Scope is full mail (https://mail.google.com/) so messages can be
permanently deleted, not just trashed.
"""
import json
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_BASE = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.settings.basic"]
CREDS_PATH = os.path.join(_BASE, "..", "credentials.json")

flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
creds = flow.run_local_server(port=0)

svc = build("gmail", "v1", credentials=creds)
email = svc.users().getProfile(userId="me").execute()["emailAddress"]
slug = email.split("@")[0]
token_path = os.path.join(_BASE, "..", f"token_gmail_{slug}.json")
with open(token_path, "w") as f:
    f.write(creds.to_json())
print(f"Authorized {email} -> {os.path.basename(token_path)}")
