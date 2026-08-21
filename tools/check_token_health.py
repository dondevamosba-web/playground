#!/usr/bin/env python3
"""
Check health of the shared Meta INSTAGRAM_ACCESS_TOKEN.

Calls Graph API /debug_token to report validity, scopes and days until expiry,
then verifies each of the 4 IG business accounts is reachable with the token.

Usage:
  python3 tools/check_token_health.py
  python3 tools/check_token_health.py --warn-days 10

Exit codes: 0 = healthy, 1 = token invalid/expired, 2 = expiring within warn window.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
GRAPH = "https://graph.facebook.com/v19.0"

ACCOUNTS = {
    "Ola Digital": os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID"),
    "Storm":       os.environ.get("STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
    "Fiestas":     os.environ.get("FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
    "Techno":      os.environ.get("TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
    "Empleo":      os.environ.get("OLA_EMPLEO_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
    "Talento USA": os.environ.get("TALENTO_USA_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
}

# Google OAuth tokens on live code paths (token_gmail.json died silently on
# 2026-07-06 and blocked job drafts for days — check them all daily)
GOOGLE_TOKENS = {
    "token_sheets.json": "sheets/drive — TODO el pipeline de contenido",
    "token_gmail.json":  "gmail — drafts de job outreach y briefings",
}


def check_google_tokens() -> bool:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    ok = True
    print("\nGoogle tokens:")
    for fname, what in GOOGLE_TOKENS.items():
        path = ROOT / fname
        if not path.exists():
            print(f"  ❌ {fname}: no existe — {what}")
            ok = False
            continue
        try:
            creds = Credentials.from_authorized_user_file(str(path))
            creds.refresh(Request())
            print(f"  ✅ {fname}: refresh OK")
        except Exception as e:
            print(f"  ❌ {fname}: {str(e)[:90]} — {what}")
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-days", type=int, default=10)
    args = parser.parse_args()

    r = requests.get(f"{GRAPH}/debug_token",
                     params={"input_token": TOKEN, "access_token": TOKEN},
                     timeout=30)
    data = r.json().get("data", {})

    if not data.get("is_valid"):
        print("❌ TOKEN INVALID — all posting is down.")
        print(f"   Error: {data.get('error', r.json().get('error', 'unknown'))}")
        print("   Re-issue a long-lived token in Meta Business Suite → System Users,")
        print("   then update INSTAGRAM_ACCESS_TOKEN in .env")
        sys.exit(1)

    expires_at = data.get("expires_at", 0)
    if expires_at == 0:
        expiry_msg = "never (system-user token)"
        days_left = None
    else:
        exp = datetime.fromtimestamp(expires_at, tz=timezone.utc)
        days_left = (exp - datetime.now(timezone.utc)).days
        expiry_msg = f"{exp:%Y-%m-%d} ({days_left} days left)"

    print(f"Token valid: yes")
    print(f"Type:        {data.get('type', '?')} / app {data.get('application', '?')}")
    print(f"Expires:     {expiry_msg}")
    print(f"Scopes:      {', '.join(data.get('scopes', []))}")

    print("\nAccount reachability:")
    all_ok = True
    for name, ig_id in ACCOUNTS.items():
        if not ig_id:
            print(f"  ⚠️  {name}: no business account ID in .env")
            all_ok = False
            continue
        ar = requests.get(f"{GRAPH}/{ig_id}",
                          params={"fields": "username", "access_token": TOKEN},
                          timeout=30)
        if ar.ok:
            print(f"  ✅ {name}: @{ar.json().get('username', '?')}")
        else:
            err = ar.json().get("error", {}).get("message", ar.text[:120])
            print(f"  ❌ {name}: {err}")
            all_ok = False

    google_ok = check_google_tokens()

    if days_left is not None and days_left < args.warn_days:
        print(f"\n⚠️  Token expires in {days_left} days — re-issue soon "
              "(Meta Business Suite → System Users → Generate token, update .env).")
        sys.exit(2)
    if not all_ok or not google_ok:
        sys.exit(2)
    print("\nAll healthy.")


if __name__ == "__main__":
    main()
