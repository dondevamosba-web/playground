#!/usr/bin/env python3
"""
Content calendar for @talento.remoto.usa — latinos buscando trabajo remoto en USA.
3 posts/day: tips, skills, motivacional.

Usage:
  python3 tools/fill_content_talento_usa.py
  python3 tools/fill_content_talento_usa.py --weeks 4 --dry-run
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.claude_call import call_claude

SHEET_TITLE   = "Talento USA — Content Calendar"
SHEET_ENV_KEY = "TALENTO_USA_CALENDAR_SHEET_ID"

WEEKLY_SLOTS = [
    (0, "08:00", "single",   "Tip: cómo armar un perfil de LinkedIn para el mercado americano"),
    (0, "13:00", "carousel", "Skills más buscados por empresas de USA en latinos"),
    (0, "19:00", "single",   "Motivacional: latinos triunfando en trabajo remoto"),
    (1, "08:00", "single",   "Tip de inglés para entrevistas laborales remotas"),
    (1, "13:00", "single",   "Cuánto pagan los roles de paid ads / marketing en USA"),
    (1, "19:00", "single",   "Mito vs realidad: trabajar remotamente para USA"),
    (2, "08:00", "carousel", "Paso a paso: cómo conseguir tu primer cliente o trabajo en USA"),
    (2, "13:00", "single",   "Herramientas que usan los marketers en USA"),
    (2, "19:00", "single",   "Inspiracional: historia de éxito latino remoto"),
    (3, "08:00", "single",   "Tip: cómo presentar resultados en USD en tu portfolio"),
    (3, "13:00", "single",   "Diferencias culturales al trabajar con equipos americanos"),
    (3, "19:00", "single",   "Reflexión o quote sobre trabajo remoto"),
    (4, "08:00", "single",   "Tip para la entrevista en inglés: qué preguntan en USA"),
    (4, "13:00", "carousel", "Checklist: ¿estás listo para trabajar para USA?"),
    (4, "19:00", "single",   "CTA: postulate con @talento.remoto.usa"),
    (5, "10:00", "single",   "Dato del mercado: salarios remotos para latinos en 2025"),
    (5, "14:00", "single",   "Motivacional fin de semana: invertí en tu carrera"),
    (5, "18:00", "single",   "Tip: qué estudiar o aprender para mejorar tu perfil"),
    (6, "11:00", "single",   "Reflexión dominical: el trabajo remoto cambió todo"),
    (6, "15:00", "single",   "Inspiracional: de Latinoamérica al mercado global"),
    (6, "19:00", "single",   "Preview de la semana: tips y contenido que viene"),
]

# Rebuilt 2026-07-21: the old post_XXX_*.png pool mixed three different
# palettes (navy+lime, dark green+lime, cream+red) across the 21 unique
# designs — user flagged inconsistent composition/color. Replaced with a
# single unified navy+lime palette across all 21, built from
# talento-usa-posts.html via screenshot_talento_usa.py. Order matches
# WEEKLY_SLOTS 1:1 (post N below = WEEKLY_SLOTS[N-1]).
TRIAD_CYCLE = [
    ".tmp/talento_posts_v2/01_post_1_tip_perfil_de_linkedin.png",
    ".tmp/talento_posts_v2/02_post_2_skills_más_buscados.png",
    ".tmp/talento_posts_v2/03_post_3_motivacional_latinos_triunfando.png",
    ".tmp/talento_posts_v2/04_post_4_tip_de_inglés_para_entrevistas.png",
    ".tmp/talento_posts_v2/05_post_5_stat_cuánto_pagan.png",
    ".tmp/talento_posts_v2/06_post_6_mito_vs_realidad.png",
    ".tmp/talento_posts_v2/07_post_7_paso_a_paso_primer_cliente.png",
    ".tmp/talento_posts_v2/08_post_8_herramientas_que_usan_los_marketers_en_usa.png",
    ".tmp/talento_posts_v2/09_post_9_inspiracional_historia_de_éxito.png",
    ".tmp/talento_posts_v2/10_post_10_tip_presentar_resultados_en_usd.png",
    ".tmp/talento_posts_v2/11_post_11_diferencias_culturales.png",
    ".tmp/talento_posts_v2/12_post_12_reflexión_sobre_trabajo_remoto.png",
    ".tmp/talento_posts_v2/13_post_13_tip_entrevista_en_inglés.png",
    ".tmp/talento_posts_v2/14_post_14_checklist_estás_listo.png",
    ".tmp/talento_posts_v2/15_post_15_cta_postulate.png",
    ".tmp/talento_posts_v2/16_post_16_dato_del_mercado_salarios.png",
    ".tmp/talento_posts_v2/17_post_17_motivacional_fin_de_semana.png",
    ".tmp/talento_posts_v2/18_post_18_tip_qué_estudiar.png",
    ".tmp/talento_posts_v2/19_post_19_reflexión_dominical.png",
    ".tmp/talento_posts_v2/20_post_20_inspiracional_de_latinoamérica_al_mercado_global.png",
    ".tmp/talento_posts_v2/21_post_21_preview_de_la_semana.png",
]

HASHTAGS = (
    "#TrabajoRemoto #RemoteWork #LatinosEnUSA #TrabajoEnDolares "
    "#PaidAds #MarketingDigital #FreelanceLatam #RemoteLatam "
    "#TrabajoDesdeHouse #LatinTalent #MarketingRemoto #CarreraDigital #USA"
)

BRAND_CONTEXT = """
@talento.remoto.usa conecta profesionales latinos con empresas americanas que buscan talento remoto calificado.
Especialidad: roles digitales — paid media (Meta Ads, Google Ads), social media, copywriting, diseño UX/UI.

Audiencia: latinos de Argentina, México, Colombia, Perú y toda LATAM con habilidades digitales que quieren trabajar en dólares desde su país.
Tono: aspiracional pero práctico. Empoderador, sin ser superficial. En español neutro (puede entenderlo toda LATAM).
Meta: que los seguidores se postulen enviando su perfil por DM.
"""


def generate_caption(content_type: str, post_number: int) -> str:
    prompt = f"""Escribí un caption para Instagram de @talento.remoto.usa.

{BRAND_CONTEXT}

Tipo de contenido: {content_type}
Número de post en secuencia: {post_number}

Reglas:
- Máximo 100 palabras
- Primera línea: hook que genere aspiración o curiosidad
- 2-3 líneas de valor concreto y accionable
- CTA al final: "Postulate por DM" o "Seguinos para más"
- Sin hashtags (se agregan aparte)
- Tono empoderador, concreto, sin frases vacías
- En español neutro (entendible en toda LATAM)

Devolvé solo el texto del caption, sin comillas ni explicación."""

    return call_claude(prompt, model="haiku")


def build_rows(start: date, weeks: int, dry_run: bool) -> list[list]:
    rows = []
    post_number = 1
    for week in range(weeks):
        for weekday, time_str, post_type, content_type in WEEKLY_SLOTS:
            days_offset = (week * 7) + (weekday - start.weekday()) % 7
            post_date = start + timedelta(days=days_offset)

            if dry_run:
                caption = f"[DRY RUN] {content_type[:60]}"
            else:
                print(f"  Generando post {post_number}: {content_type[:50]}...")
                caption = generate_caption(content_type, post_number)

            media_url = TRIAD_CYCLE[(post_number - 1) % len(TRIAD_CYCLE)]
            rows.append([
                post_date.strftime("%Y-%m-%d"),
                time_str,
                post_date.strftime("%A"),
                content_type,
                post_type,
                caption,
                HASHTAGS,
                media_url,
                "pending",
                "",
            ])
            post_number += 1
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sheet-id", default=None)
    args = parser.parse_args()

    sheet_id = args.sheet_id or os.getenv(SHEET_ENV_KEY)
    if not sheet_id:
        print(f"ERROR: {SHEET_ENV_KEY} no está en .env y no se pasó --sheet-id.")
        sys.exit(1)

    start = date.today()
    days_to_monday = (7 - start.weekday()) % 7 or 7
    start = start + timedelta(days=days_to_monday)

    total = args.weeks * len(WEEKLY_SLOTS)
    print(f"Generando {total} posts en {args.weeks} semanas desde {start}...")

    rows = build_rows(start, args.weeks, args.dry_run)

    if args.dry_run:
        for row in rows:
            print(f"  {row[0]} {row[1]} [{row[4]}] {row[3][:50]}")
        print(f"\n{len(rows)} filas se escribirían en sheet {sheet_id}")
        return

    sheets, _ = get_services()
    # Header only if missing, then append — see fill_content_storm.py 2026-07-18
    # fix: a plain values().update(range="A1", ...) here overwrites whatever
    # already occupies rows 1..len(rows), destroying existing queued posts.
    header = [["Date", "Time", "Day", "Content Type", "Post Type",
               "Caption", "Hashtags", "Media URL", "Status", "Post ID"]]
    existing = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A1:J1"
    ).execute().get("values", [])
    if not existing:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="A1",
            valueInputOption="RAW",
            body={"values": header},
        ).execute()
    sheets.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()

    print(f"\nListo. {len(rows)} posts escritos:")
    print(f"  https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    main()
