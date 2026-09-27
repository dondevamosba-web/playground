# WhatsApp Digest — ordenar los 3 chats de notas

## Objetivo
Convertir los 3 chats de WhatsApp donde me mando notas a mí mismo en una lista ordenada:
tareas abiertas, checklist de la casa, links sin nota, duplicados y cosas guardadas en el chat equivocado.
El resultado se carga en el tablero de Notion **"Tablero personal (WhatsApp)"**.

## Los 3 chats y sus tags

| Chat (nombre del grupo en WhatsApp) | Qué va | Tags |
|---|---|---|
| `Psi 💭 #terapia #aprender` | Lo emocional y la terapia | `#terapia` `#aprender` |
| `Ide 🎁 #biz #cliente #aprender #postear #plata` | Negocio, contenido, aprendizaje | `#biz` `#cliente` `#aprender` `#postear` `#plata` |
| `Vida 🏠💪 #casa #compra #cuerpo` | Cuerpo, casa y compras | `#casa` `#compra` `#cuerpo` |

El nombre del grupo **tiene que empezar con** `Psi`, `Ide` o `Vida`: así lo reconoce la herramienta
(`Fit` se toma como el nombre viejo de Vida).

### Configuración personal (no va a git)
Los tags propios, los nombres de clientes y otras palabras clave personales van en
`.tmp/whatsapp_digest/config.json`, que está ignorado por git. Ejemplo:
```json
{
  "tag_alias": {"#terapia": "#mi-tag"},
  "keywords": {"#cliente": ["nombre del cliente"]},
  "aliases": {"NombreViejo": "Ide"}
}
```
Si el archivo no existe, se usan los tags genéricos de la tabla de arriba. `.tmp/` se puede borrar, así que
conviene tener una copia de este archivo fuera del repo.

Reglas al escribir:
- Un tag al principio del mensaje. Si no lo ponés, la herramienta lo infiere por palabras clave.
- Ningún link sin verbo: `postear`, `copiar`, `aprender`, `cliente`, `ver`.
- Las listas (ej. CASA — PRIORIDADES) se **editan en Notion**, no se vuelven a copiar en WhatsApp.

## Inputs
- Exportación de cada chat: WhatsApp → chat → ⋯ → Exportar chat → **Sin archivos**. Se obtiene un `.zip`.
- Opcional: `--since YYYY-MM-DD` para procesar solo lo nuevo desde la última corrida.

## Pasos
1. Correr la herramienta:
   ```
   python3 tools/whatsapp_digest.py Psi.zip Ide.zip Vida.zip --since 2026-09-27
   ```
2. Leer `.tmp/whatsapp_digest/digest.md`. Revisar a mano la sección **Fuera de lugar**: la inferencia es por
   palabras clave y puede errar.
3. Cargar en Notion (base **Pendientes** del tablero): cada tarea suelta y cada ☐ de las checklists que no
   esté ya cargado, con su tag y el chat de origen. Los links sin nota **no** se cargan: se listan en el resumen
   para que yo decida.
4. Contestar con el resumen: cuántas tareas nuevas, qué quedó fuera de lugar y cuántos links sin nota.

## Cómo corre la herramienta
- 100% local, sin APIs ni costos. Lee `.zip`, `chat.txt` o una carpeta.
- Ignora mensajes eliminados y adjuntos omitidos.
- Salidas: `.tmp/whatsapp_digest/digest.md` (para leer) y `digest.json` (para cargar).

## Casos borde y aprendizajes
- La exportación trae `chat.txt` (fechas `[M/D/YY, H:MM:SS AM]`) y `chat.md` (del que se saca el nombre del grupo).
- `#aprender` está en Psi y en Ide. Si aparece en Vida, se sugiere moverlo a Ide.
- Los textos largos y emocionales pueden tener palabras de la casa o de plata. Por eso primero se prueban los
  tags del chat propio y solo se marca "fuera de lugar" si ninguno coincide.
- Las palabras clave se comparan como palabras enteras (así "debería" no cuenta como "debe").
