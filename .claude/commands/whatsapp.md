---
description: Actualiza mis notas de WhatsApp (Psi / Ide / Vida), sincroniza Notion y propone qué hacer
argument-hint: "[--llm] [días]"
---

Seguí `workflows/personal/notes_system.md`. Pasos:

1. Corré `python3 tools/weekly_review.py --days ${1:-7}` (agregá `--llm` solo si $ARGUMENTS lo incluye: es una llamada paga).
   - Si dice "Sin fuentes nuevas", preguntame si exporté los chats a `~/Downloads/whatsapp/` o si el bridge está corriendo
     (`bash tools/whatsapp_bridge.sh status`).
   - Si dice "0 mensajes leídos", WhatsApp cambió el formato del export: avisame y no sigas.
2. Leé el `review-*.md` que generó y `.tmp/notes_rag/links.md` si hay links nuevos.
3. Usá las herramientas MCP `notas` (`propuestas`, `pendientes`, `buscar_notas`) para profundizar lo que haga falta,
   en vez de leer los archivos enteros.
4. Respondeme en español rioplatense, corto:
   - **3 cosas para hacer hoy** (concretas, de lo más viejo o repetido).
   - Lo que conviene **mover de chat** o **borrar**.
   - Si el sync con Notion creó tareas nuevas, cuáles.
   - Una línea sobre las notas de madrugada solo si hay 3 o más.
5. No mandes mensajes, no edites ni borres filas de Notion, y no me muestres el contenido de Psi salvo que lo pida.
