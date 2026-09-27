# DevEx Setup — Claude Code con Graphify, Agent Skills, Ponytail y OmniRoute

## Objetivo
Gastar menos contexto y tokens, no releer archivos, trabajar con un flujo ordenado
(spec → plan → build → test → review → ship) y no frenar cuando se termina la cuota de Claude.

## Dónde se corre
**En la Mac, en la terminal, desde la raíz del repo.** No en una sesión de Claude Code en la nube:
ese contenedor se borra y los plugins y servidores desaparecen con él.

## Pasos
```bash
cd ~/ruta/al/playground
git pull
bash tools/devex_setup.sh diagnose     # solo mira, no cambia nada
bash tools/devex_setup.sh all          # cada paso pregunta [s/N] antes de tocar algo
```
O de a uno: `backup`, `graphify`, `skills`, `ponytail`, `omniroute`, `claudemd`.

Después: reiniciar Claude Code, abrirlo en el repo y correr `/graphify .` (una vez; luego `/graphify . --update`).

| Paso | Qué instala | Dónde | Cómo se desinstala |
|---|---|---|---|
| graphify | paquete `graphifyy` (uv) + skill y 2 hooks PreToolUse | `~/.local/bin`, `.claude/skills/graphify/`, `.claude/settings.json`, `CLAUDE.md` | `bash tools/devex_setup.sh uninstall graphify` |
| skills | plugin `agent-skills@addy-agent-skills` | usuario (`~/.claude/plugins`) | `… uninstall skills` |
| ponytail | plugin `ponytail@ponytail` (hooks dentro del plugin) | usuario | `… uninstall ponytail` |
| omniroute | `npm -g omniroute`, servidor en `localhost:20128` | global + `~/.omniroute/` | `… uninstall omniroute` |
| claudemd | sección `<!-- devex-rules -->` al final de `CLAUDE.md` | repo | borrar esa sección |

Backups en `~/.claude-devex-backups/` (se hace uno automático por día antes del primer cambio).
Restaurar: `tar -xzPf ~/.claude-devex-backups/backup-FECHA.tgz`.

## Fallback con OmniRoute
1. Terminal aparte: `omniroute` → dashboard `http://localhost:20128` → Providers → conectar con **keys propias**.
2. Cuando se corta Claude: `omniroute launch` en vez de `claude`. No modifica la config normal de Claude Code.
- Las keys van en el dashboard (`~/.omniroute/`), **nunca** en archivos del repo.
- Evitar los proveedores "free Claude" y los que usan cookies web: pueden violar términos de uso.

## Aprendizajes (probado el 27/9/2026 en un sandbox)
- `graphify install --project` **mergea** `.claude/settings.json` (mantiene `permissions`, agrega `hooks`) y
  **agrega** una sección `## graphify` a `CLAUDE.md` sin borrar nada.
- Tras `uv tool install`, `graphify` no está en el PATH de la terminal actual: el script exporta `~/.local/bin`.
  `uv tool update-shell` da error si ya se corrió antes; es inofensivo.
- Los plugins se instalan sin `/plugin` interactivo con `claude plugin marketplace add` + `claude plugin install --scope user`.
- Este repo tiene `bypassPermissions` en `.claude/settings.json`: los hooks nuevos corren sin pedir confirmación.
