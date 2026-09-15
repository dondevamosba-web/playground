# Project Backlog

Selected 2026-06-11. Status: ☐ todo · ◐ in progress · ✓ done

## Instagram / Content
- ✓ #1 Cross-account content calendar — tools/build_unified_calendar.py → tab "Calendario" en el unified approval sheet, gaps en rojo
- ✓ #5 Comment auto-drafter — tools/comment_drafter.py (Graph API + Claude haiku, voz por cuenta, dedup en .tmp/replied_comment_ids.json) → .tmp/comment_replies.md
- ✓ #6 Story generator — tools/post_to_story.py (post cuadrado → story 1080×1920 con fondo blur)
- ✓ #7 Competitor watcher — tools/competitor_watcher.py + tools/competitor_watchlist.json (editar handles ahí); cron lunes 9:30
- ✓ #8 DM lead funnel — tools/storm_dm_leads.py (setup/add/touch/due/list, sheet en .env STORM_DM_LEADS_ID, follow-up a los 3 días)
- ✓ #10 Fiestas weekend stories — tools/fiestas_weekend_story.py → story "ESTE FINDE" 1080×1920 desde ra_events_captioned.json

## Storm (agency growth)
- ✓ #11 Cold outreach pipeline — tools/storm_outreach_pipeline.py (scrape→fb-ads→emails→score→drafts→log; --dry-run, --skip-scrape)
- ✓ #12 Free audit lead magnet — storm-site/audit.html (form vía FormSubmit → carminattiguido@gmail.com), live en el sitio
- ✓ #14 Proposal generator — tools/storm_proposal.py --client --vertical --budget --cpl → PDF brandeado 3 páginas
- ✓ #16 LinkedIn carousels — tools/storm_linkedin_carousel.py, 4 temas (results/playbook/trust/waste) → .tmp/linkedin_carousels/
- ✓ #17 Storm website — live on GitHub Pages: https://dondevamosba-web.github.io/storm-digital-site/ (repo dondevamosba-web/storm-digital-site, source in storm-site/)

## Techno Apple
- ✓ #21 Stock + sales ledger — tools/techno_ledger.py (setup/add/sell/list, sheet ID in .env TECHNO_LEDGER_ID, venta = costo + 70 USD)
- ✓ #23 WhatsApp catalog generator — tools/techno_whatsapp_catalog.py → .tmp/techno_catalogo_*.png (solo EN STOCK, solo precios de venta)

## Olavarría house
- ✓ #25 Contractor punch list — olavarria/punchlist.html (checklist por ambiente, fotos, localStorage, export/import JSON)
- ✓ #26 Materials price comparison — tools/materiales_precios.py (API VTEX de Easy; ML y Sodimac bloquean) → olavarria/materiales_precios.md

## Automation infrastructure
- ✓ #39 Unified approval inbox — ya existía: unified approval sheet (4 tabs) + publish_all_approved.py; ahora con tab Calendario al frente
- ✓ #33 Morning briefing — tools/morning_briefing.py --email (cola por cuenta, follow-ups DM, comentarios) → Gmail draft; cron L-V 8:30
- ✓ #35 Weekly self-audit — tools/self_audit.py --email (errores en logs, git, inventario cron) → Gmail draft; cron domingo 19:00
- ✓ #37 Backup routine — weekly zip of playground to Drive (tools/backup_playground.py, cron Mon 9am, Drive: Backups/playground, keeps 4)
- ✓ #40 WAT framework dashboard — single HTML page: workflows, tools, last activity (tools/build_wat_dashboard.py → dashboard.html)

## Not selected (parked)
2 engagement tracker · 3 best-time analyzer · 4 hashtag rotation · 9 caption A/B archive · 13 case study generator · 15 client reporting · 18 review collector · 19 provider price monitor · 20 dollar blue tracker · 22 Apple release watcher · 24 budget burn-down · 27 timeline page · 28 mood board · 29 monthly close · 30 subscription auditor · 31 statement importer · 32 net worth tracker · 34 Gmail triage · 36 photos cleanup v2 · 38 receipt OCR
