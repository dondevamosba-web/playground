#!/usr/bin/env bash
# DevEx setup for Claude Code on the Mac: Graphify, Agent Skills, Ponytail, OmniRoute.
# Every step asks before changing anything and backs up first.
# Commands come from each tool's official README (checked 2026-09-27).
#
# Usage (from the repo root):
#   bash tools/devex_setup.sh diagnose        # read-only: what's installed
#   bash tools/devex_setup.sh backup          # backup ~/.claude/settings.json, .claude/, CLAUDE.md
#   bash tools/devex_setup.sh graphify        # a) graph of this repo (project scope)
#   bash tools/devex_setup.sh skills          # b) Agent Skills plugin (user scope)
#   bash tools/devex_setup.sh ponytail        # c) Ponytail plugin (user scope, own hooks)
#   bash tools/devex_setup.sh omniroute       # d) OmniRoute gateway (fallback when Claude quota runs out)
#   bash tools/devex_setup.sh claudemd        # add the work rules to CLAUDE.md
#   bash tools/devex_setup.sh all             # all of the above, in order
#   bash tools/devex_setup.sh uninstall <graphify|skills|ponytail|omniroute>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$HOME/.claude-devex-backups"
MARKER="<!-- devex-rules -->"

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }
ask()  { read -r -p "$* [s/N] " a; [[ "$a" =~ ^[sSyY]$ ]]; }

diagnose() {
  say "Sistema"
  sw_vers 2>/dev/null || uname -sr
  for c in claude node npm python3 uv git; do
    printf '  %-8s %s\n' "$c" "$(have $c && ($c --version 2>/dev/null | head -1) || echo '— no instalado')"
  done
  say "Claude Code"
  for f in "$HOME/.claude/settings.json" "$ROOT/.claude/settings.json" "$ROOT/CLAUDE.md"; do
    printf '  %-50s %s\n' "$f" "$([ -f "$f" ] && echo existe || echo no existe)"
  done
  if [ -f "$HOME/.claude/settings.json" ] && have python3; then
    python3 -c 'import json,sys; h=json.load(open(sys.argv[1])).get("hooks",{}); print("  hooks de usuario:", ", ".join(h) or "ninguno")' "$HOME/.claude/settings.json"
  fi
  have claude && { say "Plugins"; claude plugin list 2>/dev/null || true; }
  have graphify && echo "  graphify: $(graphify --version 2>/dev/null)"
  have omniroute && echo "  omniroute: instalado"
  grep -q "$MARKER" "$ROOT/CLAUDE.md" 2>/dev/null && echo "  CLAUDE.md: reglas DevEx ya agregadas"
  return 0
}

backup() {
  mkdir -p "$BACKUP_DIR"
  local out="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tgz"
  local items=()
  [ -f "$HOME/.claude/settings.json" ] && items+=("$HOME/.claude/settings.json")
  [ -d "$ROOT/.claude" ] && items+=("$ROOT/.claude")
  [ -f "$ROOT/CLAUDE.md" ] && items+=("$ROOT/CLAUDE.md")
  tar -czPf "$out" "${items[@]}"
  say "Backup → $out"
  echo "  Restaurar: tar -xzPf \"$out\""
}

ensure_backup() {
  ls "$BACKUP_DIR"/backup-"$(date +%Y%m%d)"-*.tgz >/dev/null 2>&1 || backup
}

step_graphify() {
  say "a) Graphify — grafo del repo para no releer archivos"
  echo "  Instala el paquete 'graphifyy' (doble y) con uv y registra la skill SOLO en este repo (.claude/skills/graphify/)."
  ask "¿Instalar?" || return 0
  ensure_backup
  if ! have uv; then
    echo "  Falta uv. README: 'curl -LsSf https://astral.sh/uv/install.sh | sh' (o 'brew install uv')."
    ask "¿Instalar uv con brew?" && brew install uv || { echo "  Instalá uv y volvé a correr este paso."; return 0; }
  fi
  uv tool install graphifyy
  if ! have graphify; then
    uv tool update-shell || true           # for future terminals
    export PATH="$HOME/.local/bin:$PATH"     # for this one
  fi
  (cd "$ROOT" && graphify install --project)
  grep -qx 'graphify-out/' "$ROOT/.gitignore" || printf '\n# Graphify\ngraphify-out/\n' >> "$ROOT/.gitignore"
  echo "  ✓ Listo. Abrí Claude Code en este repo y corré:  /graphify ."
  echo "    Después, para actualizar solo lo cambiado:     /graphify . --update"
}

step_skills() {
  say "b) Agent Skills — flujo spec → plan → build → test → review → ship"
  echo "  Plugin a nivel USUARIO (sirve en todos tus proyectos)."
  ask "¿Instalar?" || return 0
  ensure_backup
  claude plugin marketplace add addyosmani/agent-skills
  claude plugin install agent-skills@addy-agent-skills --scope user
  echo "  ✓ Comandos: /spec /plan /build /test /review /ship"
  echo "  Si falla con 'Permission denied (publickey)': git config --global url.\"https://github.com/\".insteadOf git@github.com:"
}

step_ponytail() {
  say "c) Ponytail — código mínimo"
  echo "  Plugin a nivel USUARIO. Trae sus 2 hooks de inicio adentro del plugin: NO toca tus hooks de settings.json."
  have node || { echo "  Falta node en el PATH (lo necesitan sus hooks)."; return 0; }
  ask "¿Instalar?" || return 0
  ensure_backup
  claude plugin marketplace add DietrichGebert/ponytail
  claude plugin install ponytail@ponytail --scope user
  echo "  ✓ Comandos: /ponytail /ponytail-review /ponytail-audit"
}

step_omniroute() {
  say "d) OmniRoute — seguir laburando cuando se corta la cuota de Claude"
  cat <<'EOF'
  Qué hace: servidor local (localhost:20128) que manda los pedidos a otros modelos.
  ⚠ Tu código pasa por proveedores de terceros. Recomendado: SOLO proveedores con API key propia
    (no los "free Claude" ni los que usan cookies web: pueden violar términos de uso).
  No escribe nada en este repo. Las keys se cargan en su dashboard y quedan en ~/.omniroute/.
EOF
  ask "¿Instalar con npm -g?" || return 0
  npm install -g omniroute
  cat <<'EOF'
  ✓ Instalado. Para usarlo:
    1. En otra terminal:  omniroute          (dashboard en http://localhost:20128)
    2. Dashboard → Providers → conectá tus proveedores con tus keys.
    3. Cuando se te acabe la cuota de Claude, en vez de 'claude' corré:
         omniroute launch
       (arranca Claude Code apuntando a OmniRoute; tu config normal de Claude no se toca)
  Opcional, atajo en tu ~/.zshrc (lo agregás vos):
    alias claude-fallback='omniroute launch'
EOF
}

step_claudemd() {
  say "Reglas de trabajo en CLAUDE.md"
  if grep -q "$MARKER" "$ROOT/CLAUDE.md" 2>/dev/null; then echo "  Ya están."; return 0; fi
  echo "  Agrega una sección al final de CLAUDE.md (no borra nada de lo que ya tiene)."
  ask "¿Agregar?" || return 0
  ensure_backup
  cat >> "$ROOT/CLAUDE.md" <<EOF

$MARKER
## Reglas DevEx (Graphify · Agent Skills · Ponytail · OmniRoute)

- **Antes de leer archivos**, consultá el grafo: \`graphify query "<pregunta>"\` o \`graphify-out/GRAPH_REPORT.md\`. Leé solo lo que el grafo señale. Si el grafo está viejo: \`/graphify . --update\`.
- **Toda tarea no trivial** sigue \`/spec → /plan → /build → /test → /review → /ship\` y deja el entregable de cada etapa. Las tareas triviales (un typo, un rename) van directo.
- **Código mínimo**: justificá cada archivo o función nueva. Nada de abstracciones sin necesidad (\`/ponytail-review\` antes de cerrar).
- **Modelos**: arquitectura y decisiones → Claude. Lo mecánico (boilerplate, tests simples) se puede derivar a un modelo más barato vía OmniRoute.
- **Salidas largas** de herramientas: resumilas, no las pegues enteras al contexto.
EOF
  echo "  ✓ Agregado."
}

uninstall() {
  case "${1:-}" in
    graphify)
      rm -rf "$ROOT/.claude/skills/graphify"; uv tool uninstall graphifyy || true
      echo "  (graphify-out/ quedó; borralo si querés: rm -rf graphify-out)";;
    skills)    claude plugin uninstall agent-skills@addy-agent-skills; claude plugin marketplace remove addy-agent-skills || true;;
    ponytail)  claude plugin uninstall ponytail@ponytail; claude plugin marketplace remove ponytail || true
               rm -f "$HOME/.claude/.ponytail-active";;
    omniroute) npm uninstall -g omniroute; echo "  Datos y keys quedan en ~/.omniroute (borrar: rm -rf ~/.omniroute)";;
    *) echo "uninstall <graphify|skills|ponytail|omniroute>"; exit 1;;
  esac
}

case "${1:-}" in
  diagnose)  diagnose ;;
  backup)    backup ;;
  graphify)  step_graphify ;;
  skills)    step_skills ;;
  ponytail)  step_ponytail ;;
  omniroute) step_omniroute ;;
  claudemd)  step_claudemd ;;
  all)       diagnose; backup; step_graphify; step_skills; step_ponytail; step_omniroute; step_claudemd
             say "Listo. Reiniciá Claude Code y corré: bash tools/devex_setup.sh diagnose" ;;
  uninstall) uninstall "${2:-}" ;;
  *) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
