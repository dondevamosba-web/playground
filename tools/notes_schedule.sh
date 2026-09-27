#!/usr/bin/env bash
# Schedules the notes system on macOS (launchd):
#   - Sunday 10:00  → tools/weekly_review.py   (update + links + Notion + proposals + notification)
#   - every hour    → tools/notion_sync.py     (only if NOTION_TOKEN is in .env)
#
# Usage:
#   bash tools/notes_schedule.sh install
#   bash tools/notes_schedule.sh status
#   bash tools/notes_schedule.sh uninstall
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$(command -v python3)"
AGENTS="$HOME/Library/LaunchAgents"
LOGS="$ROOT/.tmp/notes_rag/logs"

plist() {  # label, script, schedule-xml
  cat > "$AGENTS/$1.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$ROOT/tools/$2</string></array>
  <key>WorkingDirectory</key><string>$ROOT</string>
  $3
  <key>StandardOutPath</key><string>$LOGS/$1.log</string>
  <key>StandardErrorPath</key><string>$LOGS/$1.log</string>
</dict>
</plist>
EOF
  launchctl unload "$AGENTS/$1.plist" 2>/dev/null || true
  launchctl load "$AGENTS/$1.plist"
  echo "  ✓ $1"
}

case "${1:-}" in
  install)
    mkdir -p "$AGENTS" "$LOGS"
    plist com.notas.weekly-review weekly_review.py \
      '<key>StartCalendarInterval</key><dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>'
    if grep -q '^NOTION_TOKEN=' "$ROOT/.env" 2>/dev/null; then
      plist com.notas.notion-sync notion_sync.py '<key>StartInterval</key><integer>3600</integer>'
    else
      echo "  – Sync horario con Notion no instalado: falta NOTION_TOKEN en .env"
    fi
    echo "  Logs: $LOGS" ;;
  status)
    launchctl list | grep com.notas || echo "  Nada programado" ;;
  uninstall)
    for l in com.notas.weekly-review com.notas.notion-sync; do
      launchctl unload "$AGENTS/$l.plist" 2>/dev/null || true
      rm -f "$AGENTS/$l.plist"
    done
    echo "  ✓ Desprogramado" ;;
  *) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
