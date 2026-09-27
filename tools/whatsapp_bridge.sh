#!/usr/bin/env bash
# WhatsApp bridge (read-only) for the notes RAG — macOS.
#
# Uses the Go bridge from github.com/lharries/whatsapp-mcp pinned to a reviewed commit, with its
# REST server (/api/send, bound to every interface with no auth) PATCHED OUT: nothing can send
# messages through it. It syncs your WhatsApp into ~/whatsapp-mcp/whatsapp-bridge/store/messages.db;
# tools/notes_rag.py reads only YOUR messages in the Psi / Ide / Vida chats from there.
#
# ⚠ It links as a WhatsApp "linked device" through an unofficial library (whatsmeow).
#   WhatsApp can log it out or restrict the account. The local DB stores ALL your chats.
#
# Usage:
#   bash tools/whatsapp_bridge.sh install     # clone + patch + build
#   bash tools/whatsapp_bridge.sh link        # first run: scan the QR with your phone
#   bash tools/whatsapp_bridge.sh start       # keep it running in the background (launchd)
#   bash tools/whatsapp_bridge.sh status
#   bash tools/whatsapp_bridge.sh stop
#   bash tools/whatsapp_bridge.sh uninstall
set -euo pipefail

REPO="https://github.com/lharries/whatsapp-mcp.git"
COMMIT="7d6a06d"                                   # reviewed 2026-09-27
DIR="${WHATSAPP_BRIDGE_HOME:-$HOME/whatsapp-mcp}"
BRIDGE="$DIR/whatsapp-bridge"
LABEL="com.notas.whatsapp-bridge"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ask() { read -r -p "$* [s/N] " a; [[ "$a" =~ ^[sSyY]$ ]]; }

install() {
  say "Instalar el bridge de WhatsApp (solo lectura)"
  sed -n '9,10p' "$0" | sed 's/^# \{0,1\}//'
  ask "¿Seguir?" || exit 0
  command -v go >/dev/null || { ask "Falta Go. ¿Instalarlo con brew?" && brew install go || exit 1; }
  [ -d "$DIR/.git" ] || git clone -q "$REPO" "$DIR"
  git -C "$DIR" fetch -q origin && git -C "$DIR" checkout -q "$COMMIT"
  # Remove the unauthenticated REST server (send messages / download media).
  sed -i '' 's|^	startRESTServer(client, messageStore, 8080)$|	// startRESTServer disabled: read-only bridge (no /api/send). Patched by tools/whatsapp_bridge.sh|' "$BRIDGE/main.go"
  if grep -q '^	startRESTServer(' "$BRIDGE/main.go"; then
    echo "  ✗ No se pudo desactivar el servidor REST. No compilo." ; exit 1
  fi
  (cd "$BRIDGE" && go build -o whatsapp-bridge .)
  echo "  ✓ Compilado en $BRIDGE/whatsapp-bridge (servidor REST desactivado)"
  echo "  Siguiente: bash tools/whatsapp_bridge.sh link"
}

link() {
  say "Vincular: escaneá el QR con WhatsApp → Dispositivos vinculados → Vincular dispositivo"
  echo "  Cuando diga que se conectó y termine de sincronizar, cortá con Ctrl+C y corré 'start'."
  cd "$BRIDGE" && ./whatsapp-bridge
}

start() {
  mkdir -p "$(dirname "$PLIST")" "$BRIDGE/store"
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$BRIDGE/whatsapp-bridge</string></array>
  <key>WorkingDirectory</key><string>$BRIDGE</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$BRIDGE/store/bridge.log</string>
  <key>StandardErrorPath</key><string>$BRIDGE/store/bridge.log</string>
</dict>
</plist>
EOF
  launchctl unload "$PLIST" 2>/dev/null || true
  launchctl load "$PLIST"
  echo "  ✓ Corriendo en segundo plano (arranca solo al prender la Mac). Log: $BRIDGE/store/bridge.log"
}

status() {
  launchctl list | grep -q "$LABEL" && echo "  bridge: corriendo" || echo "  bridge: parado"
  local db="$BRIDGE/store/messages.db"
  if [ -f "$db" ]; then
    echo "  DB: $(du -h "$db" | cut -f1) · último mensaje: $(sqlite3 "$db" 'select max(timestamp) from messages' 2>/dev/null)"
  else
    echo "  DB: todavía no existe (falta 'link')"
  fi
  tail -3 "$BRIDGE/store/bridge.log" 2>/dev/null || true
}

stop() {
  launchctl unload "$PLIST" 2>/dev/null || true
  echo "  ✓ Parado"
}

uninstall() {
  stop
  rm -f "$PLIST"
  echo "  Acordate de sacar el dispositivo en WhatsApp → Dispositivos vinculados."
  if ask "¿Borrar también $DIR (incluye la base con TODOS tus mensajes)?"; then rm -rf "$DIR"; fi
}

case "${1:-}" in
  install|link|start|status|stop|uninstall) "$1" ;;
  *) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
