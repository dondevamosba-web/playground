#!/bin/bash
set -euo pipefail

# Only needed in Claude Code on the web — local sessions already have these files.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Recreate the Google OAuth token (used by tools/sheets_client.py) from a
# base64-encoded env var, since the raw file is gitignored and can't be committed.
if [ -n "${TOKEN_SHEETS_JSON_B64:-}" ] && [ ! -f token_sheets.json ]; then
  echo "$TOKEN_SHEETS_JSON_B64" | base64 -d > token_sheets.json
fi

python3 -m pip install -q --ignore-installed -r requirements.txt
