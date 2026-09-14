# Workflow: Panel Social (dashboard local)

**Qué es:** Dashboard local de una sola página con las 4 cuentas (Ola Digital, Storm, Fiestas, Techno): seguidores y crecimiento día/semana/mes, últimos posteos, botón de sugerencias con Claude, y acceso rápido a WhatsApp Web.

**Trigger:** Manual — abrilo cuando quieras ver cómo van las cuentas.

---

## Correrlo

```bash
python3 tools/social_dashboard_server.py
```

Abrir: http://localhost:5056

Requiere lo mismo que `tools/post_instagram.py` (`INSTAGRAM_ACCESS_TOKEN` + el ID de cada cuenta) más `ANTHROPIC_API_KEY` para el botón de Mejoras. Una cuenta sin su ID en `.env` se muestra igual, marcada como "no configurada", sin romper el resto de la página.

## Cómo funciona el crecimiento día a día

Cada vez que se abre la página, guarda un snapshot de seguidores/posts del día en `.tmp/social_stats_history.jsonl`. Con eso arma los badges de 1d/7d/30d y el sparkline. Si un día nadie abre el dashboard, no queda registro — para eso está `tools/snapshot_social_stats.py`, pensado para correr una vez por día vía cron si querés el historial completo sin depender de abrir la página.

```bash
python3 tools/snapshot_social_stats.py
```

## WhatsApp

El botón de WhatsApp abre `web.whatsapp.com` en una pestaña nueva — **no está embebido adentro del dashboard** porque WhatsApp bloquea que lo carguen en un iframe (X-Frame-Options de Meta). Integrarlo de verdad adentro de la página requeriría una librería no oficial (tipo `whatsapp-web.js`), que es una pieza de trabajo aparte — queda pendiente para una fase 2 si hace falta.

## Botón de Mejoras

Le manda a Claude (Sonnet, vía `tools/claude_call.py`) las estadísticas actuales + últimos posteos de la cuenta, y devuelve 4-6 sugerencias concretas basadas en esos datos (no genéricas). Cada click es una llamada a la API de Anthropic — tiene costo, aunque mínimo con Haiku/Sonnet.

## Pendiente / Fase 2

- Conectar el botón de Mejoras (o uno nuevo) a esta sesión de Claude Code para que implemente los cambios sugeridos directamente, en vez de solo mostrarlos como texto. No está resuelto todavía — hay que decidir cómo la app dispara una tarea hacia Claude Code (¿un webhook local? ¿el CLI en modo `-p`?) antes de construirlo.
- WhatsApp embebido de verdad (requiere librería no oficial, sesión persistente, etc.)

## Troubleshooting

**Una cuenta aparece "no configurada":** falta el ID de esa cuenta en `.env` (el nombre exacto de la key aparece en la tarjeta).

**Mejoras tira error:** revisar `ANTHROPIC_API_KEY` en `.env`.

**El crecimiento muestra "—" en todos lados:** normal el primer día — hace falta al menos un snapshot previo para calcular la diferencia. Al día siguiente ya va a mostrar el 1d.
