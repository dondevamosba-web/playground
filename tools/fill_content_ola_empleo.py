#!/usr/bin/env python3
"""
Content calendar for @olavarria.empleo — consultora RRHH Olavarría.
3 posts/day: tips laborales, sectores que contratan, motivacional.

Usage:
  python3 tools/fill_content_ola_empleo.py
  python3 tools/fill_content_ola_empleo.py --weeks 4 --dry-run
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

SHEET_TITLE   = "Ola Empleo — Content Calendar"
SHEET_ENV_KEY = "OLA_EMPLEO_CALENDAR_SHEET_ID"

# 3 posts por día, todos los días
WEEKLY_SLOTS = [
    (0, "08:00", "single",   "Tip para postulantes: cómo mejorar el CV"),
    (0, "13:00", "carousel", "Sectores que están contratando en Olavarría"),
    (0, "19:00", "single",   "Motivacional o reflexión sobre el trabajo"),
    (1, "08:00", "single",   "Tip entrevista laboral"),
    (1, "13:00", "single",   "Perfil buscado: qué piden las empresas"),
    (1, "19:00", "single",   "Dato o stat del mercado laboral"),
    (2, "08:00", "carousel", "Mito vs realidad del mercado laboral"),
    (2, "13:00", "single",   "Tip: cómo destacarse entre candidatos"),
    (2, "19:00", "single",   "Motivacional laboral"),
    (3, "08:00", "single",   "Qué hace una consultora de RRHH y cómo te ayuda"),
    (3, "13:00", "single",   "Sectores industriales: Loma Negra, Cemento Avellaneda"),
    (3, "19:00", "single",   "Reflexión o quote sobre empleo"),
    (4, "08:00", "single",   "Tip para el primer día en un trabajo nuevo"),
    (4, "13:00", "carousel", "Pasos para postularse: proceso simple"),
    (4, "19:00", "single",   "CTA: mandanos tu CV"),
    (5, "10:00", "single",   "Dato del fin de semana: mercado laboral local"),
    (5, "14:00", "single",   "Motivacional fin de semana"),
    (5, "18:00", "single",   "Tip: cómo prepararse para la semana laboral"),
    (6, "11:00", "single",   "Reflexión dominical sobre carrera y trabajo"),
    (6, "15:00", "single",   "Inspiracional: casos de crecimiento profesional"),
    (6, "19:00", "single",   "Preview de la semana: qué viene"),
]

# Rebuilt 2026-07-18: old TRIAD_CYCLE pointed at .tmp/empleo_posts/ (never
# existed on disk) and cycled by post_number regardless of topic, so the
# same image kept landing next to unrelated captions ("incongruentes" per
# user report). New pool exported from ola-empleo-posts.html via
# screenshot_ola_empleo.py; matched to content_type by keyword below.
IMG_PRESENTACION = ".tmp/empleo_posts_v2/01_post_1_presentación_variante_whatsapp.png"
IMG_STAT         = ".tmp/empleo_posts_v2/02_post_2_stat_tiempo_de_búsqueda.png"
IMG_ENTREVISTA    = ".tmp/empleo_posts_v2/03_post_3_tips_entrevista.png"
IMG_CONSULTORA    = ".tmp/empleo_posts_v2/04_post_4_qué_hace_la_consultora.png"
IMG_PRIMER_DIA    = ".tmp/empleo_posts_v2/05_post_5_pasos_primer_día.png"
IMG_MITO          = ".tmp/empleo_posts_v2/06_post_6_mito_vs_realidad_sueldo.png"
IMG_MOTIVACIONAL  = ".tmp/empleo_posts_v2/07_post_7_quote_motivacional_constancia.png"
IMG_PERFIL        = ".tmp/empleo_posts_v2/08_post_8_perfil_buscado_industria.png"
IMG_CTA           = ".tmp/empleo_posts_v2/09_post_9_cta_whatsapp_directo.png"

# Fallback cycle for content_types that don't match a keyword below.
TRIAD_CYCLE = [IMG_PRESENTACION, IMG_STAT, IMG_ENTREVISTA, IMG_CONSULTORA,
               IMG_PRIMER_DIA, IMG_MITO, IMG_MOTIVACIONAL, IMG_PERFIL, IMG_CTA]

# (substring to match in content_type, lowercased) -> image. Checked in order.
KEYWORD_IMAGE_MAP = [
    ("mito", IMG_MITO),
    ("realidad", IMG_MITO),
    ("entrevista", IMG_ENTREVISTA),
    ("primer día", IMG_PRIMER_DIA),
    ("postularse", IMG_PRIMER_DIA),
    ("consultora", IMG_CONSULTORA),
    ("perfil buscado", IMG_PERFIL),
    ("sector", IMG_PERFIL),
    ("industria", IMG_PERFIL),
    ("cta", IMG_CTA),
    ("mandanos tu cv", IMG_CTA),
    ("preview de la semana", IMG_CTA),
    ("dato", IMG_STAT),
    ("stat", IMG_STAT),
    ("motivacional", IMG_MOTIVACIONAL),
    ("reflexión", IMG_MOTIVACIONAL),
    ("inspiracional", IMG_MOTIVACIONAL),
]


def pick_media(content_type: str, post_number: int) -> str:
    lc = content_type.lower()
    for kw, img in KEYWORD_IMAGE_MAP:
        if kw in lc:
            return img
    return TRIAD_CYCLE[(post_number - 1) % len(TRIAD_CYCLE)]

HASHTAGS = (
    "#OlavarríaEmpleo #EmpleoOlavarría #BúsquedaLaboral #Olavarría "
    "#RRHH #RecursosHumanos #Empleo #TrabajoArgentina #BúsquedaDeEmpleo "
    "#LomaNegra #IndustriaOlavarría #EmpleoLocal #Postulaciones #CV"
)

BRAND_CONTEXT = """
@olavarria.empleo es una consultora de RRHH en Olavarría, Buenos Aires, Argentina.
Conecta candidatos calificados con empresas industriales locales: Loma Negra, Cemento Avellaneda, fábricas y talleres.

Audiencia: profesionales y técnicos del mercado local que buscan trabajo o quieren mejorar su situación laboral.
Tono: cercano, profesional, empático. En español rioplatense (vos, ustedes).
Meta: posicionarse como la consultora de referencia en Olavarría y conseguir que candidatos manden su CV.
El servicio es gratuito para los candidatos.
"""


CAPTION_TEMPLATES = {
    "Tip para postulantes: cómo mejorar el CV": [
        "¿Tu CV no está generando respuestas? Revisá estas 3 cosas antes de mandarlo:\n\n1. Foto profesional y contacto actualizado\n2. Experiencia clara con logros, no solo tareas\n3. Que no supere 2 páginas\n\nMandanos tu CV por DM y te damos feedback gratis.",
        "El CV es tu primera impresión. Hacela contar.\n\nEmpezá por el objetivo: 2 líneas que expliquen quién sos y qué buscás. Después la experiencia más relevante, siempre con resultados concretos.\n\nMandanos tu CV por DM y lo vemos juntos.",
        "Un CV bien hecho multiplica tus chances. Los errores más comunes: falta de foto, diseño desprolijo, experiencias sin contexto.\n\nHacelo simple, claro y honesto. Las empresas valoran la claridad.\n\nMandanos tu CV por DM.",
        "¿Sabés cuántos segundos tiene un CV para convencer a un reclutador? Menos de 10.\n\nTitulo, experiencia clave y habilidades concretas arriba. Lo demás después.\n\nMandanos el tuyo por DM y te ayudamos.",
    ],
    "Sectores que están contratando en Olavarría": [
        "Olavarría tiene sectores que contratan todo el año. En este momento:\n\n• Industria cementera (Loma Negra, Cemento Avellaneda)\n• Logística y transporte\n• Mantenimiento industrial y oficios técnicos\n\n¿Tenés experiencia en alguno? Mandanos tu CV por DM.",
        "La industria local no para. Loma Negra y las plantas cementeras buscan operarios, técnicos y administrativos de forma constante.\n\nSi tenés ganas de trabajar, hay lugar.\n\nSeguinos para ver todas las búsquedas activas.",
        "Tres sectores con búsquedas abiertas esta semana en Olavarría:\n\n1. Producción y planta\n2. Administración y logística\n3. Seguridad e higiene industrial\n\nMandanos tu perfil por DM y te orientamos.",
        "¿Buscás trabajo estable en Olavarría? La industria local está contratando. Operarios, técnicos y perfiles administrativos con experiencia o sin ella.\n\nMandanos tu CV por DM y te conectamos.",
    ],
    "Motivacional o reflexión sobre el trabajo": [
        "Buscar trabajo cansa. Pero cada CV que mandás es un paso más cerca.\n\nNo te rindas. El proceso tiene tiempos que no siempre controlamos.\n\nSeguinos para tips que te ayuden en el camino.",
        "El trabajo ideal no existe, pero el trabajo correcto sí.\n\nEl correcto es el que te permite crecer, pagar tus cuentas y levantarte con ganas.\n\nSeguinos para más consejos laborales.",
        "A veces el 'no' no es un rechazo. Es una redirección.\n\nCada proceso de selección que no termina bien te prepara mejor para el siguiente.\n\nSeguinos para más tips.",
        "El primer paso siempre es el más difícil. Pero si ya estás buscando, ya estás avanzando.\n\nMandanos tu CV por DM y te acompañamos en el proceso.",
    ],
    "Tip entrevista laboral": [
        "Antes de una entrevista, investigá la empresa. Mínimo: qué hace, cuántos empleados tiene, qué valoran.\n\nEso solo ya te diferencia del 80% de los candidatos.\n\nSeguinos para más tips de entrevista.",
        "En la entrevista te van a preguntar por qué querés trabajar ahí. Preparate una respuesta real.\n\nNo es trampa. Es que las empresas quieren gente que quiera estar, no que necesite estar.\n\nSeguinos para más consejos.",
        "Llegá 10 minutos antes. Traé el CV impreso aunque lo mandaste por mail. Mirá a los ojos.\n\nCosas básicas que marcan la diferencia en una entrevista.\n\nSeguinos para más tips.",
        "¿Te preguntaron cuánto querés ganar y no supiste qué decir? Investigá el rango del puesto antes.\n\nGlassdoor, LinkedIn, o directamente preguntándonos a nosotros.\n\nMandanos un DM y te orientamos.",
    ],
    "Perfil buscado: qué piden las empresas": [
        "Las empresas de Olavarría buscan algo que no siempre está en el CV: actitud.\n\nPuntualidad, comunicación clara, ganas de aprender. Eso vale tanto como la experiencia.\n\nMandanos tu CV por DM.",
        "¿Qué buscan las industrias locales? Técnicos con experiencia en planta, operarios con registro, y perfiles administrativos que manejen Excel básico.\n\n¿Te identificás? Mandanos tu CV por DM.",
        "Perfil más buscado esta semana: técnico en mantenimiento mecánico o eléctrico con experiencia en industria.\n\nSi sos vos o conocés a alguien, mandanos el CV por DM.",
        "Las empresas no solo miran el título. Miran el historial, la estabilidad y las referencias.\n\nArmá bien tu perfil y explicá cada salida laboral con contexto real.\n\nSeguinos para más tips.",
    ],
    "Dato o stat del mercado laboral": [
        "Dato: el 60% de los puestos laborales se cubren antes de publicarse, por recomendaciones internas.\n\nPor eso importa tener tu CV en una consultora activa como la nuestra.\n\nMandanos el tuyo por DM.",
        "En Argentina, los procesos de selección duran entre 2 y 6 semanas en promedio para posiciones industriales.\n\nTener el CV actualizado y listo acelera tu ingreso al proceso.\n\nMandanos el tuyo por DM.",
        "El 70% de las búsquedas laborales en industria requieren al menos secundario completo y no exigen título universitario.\n\nLa experiencia y la actitud cuentan igual o más.\n\nSeguinos para más datos.",
        "¿Sabías que Olavarría tiene una de las tasas de empleo industrial más altas de la provincia?\n\nLa industria cementera, los servicios y el comercio sostienen el mercado local.\n\nSeguinos para estar al día.",
    ],
    "Mito vs realidad del mercado laboral": [
        "MITO: Hay que tener contactos para conseguir trabajo.\nREALIDAD: Los contactos ayudan, pero un CV bien armado y actitud proactiva abren puertas igualmente.\n\nSeguinos para más tips reales.",
        "MITO: Si no tenés título no te toman.\nREALIDAD: En industria, la experiencia técnica y los oficios son igual de valorados que el título.\n\nMandanos tu CV por DM sin importar tu formación.",
        "MITO: Solo contratan a menores de 35.\nREALIDAD: La madurez laboral y la estabilidad son muy valoradas en industria.\n\nMandanos tu perfil por DM, hay búsquedas para todos los rangos.",
        "MITO: Una consultora cobra por encontrarte trabajo.\nREALIDAD: Para los candidatos es gratis. Siempre.\n\nMandanos tu CV por DM y empezamos.",
    ],
    "Tip: cómo destacarse entre candidatos": [
        "¿Cómo destacarse en un proceso con muchos candidatos? Personalizá tu CV para cada búsqueda.\n\nNo mandes siempre el mismo. Resaltá lo más relevante para ese puesto.\n\nSeguinos para más tips.",
        "Un detalle que pocos hacen: el mail de postulación. Escribí 3 líneas explicando por qué querés ese puesto.\n\nTarda 5 minutos y te diferencia de todos los que solo adjuntan el CV.\n\nSeguinos para más.",
        "En una entrevista grupal, el que habla primero no siempre gana. El que escucha, suma y responde claro sí.\n\nAprendé a leer el momento. Eso es inteligencia emocional laboral.\n\nSeguinos para más tips.",
        "Seguí en contacto después de la entrevista. Un mail agradeciendo y reafirmando tu interés al día siguiente marca diferencia.\n\nPocos lo hacen. Vos podés ser de esos pocos.\n\nSeguinos para más tips.",
    ],
    "Motivacional laboral": [
        "El trabajo no define quién sos. Pero sí dice mucho de lo que valorás.\n\nBuscá uno donde puedas crecer, no solo sobrevivir.\n\nSeguinos para tips que te ayuden en esa búsqueda.",
        "No hay empleo pequeño cuando se hace con compromiso.\n\nCada rol bien hecho abre la puerta al siguiente.\n\nSeguinos para más reflexiones laborales.",
        "La paciencia en la búsqueda laboral es una habilidad. No todos la tienen.\n\nSi estás en el proceso, ya estás haciendo lo correcto.\n\nSeguinos para acompañarte.",
        "Cambiar de trabajo da miedo. Quedarse en uno que no te hace bien también.\n\nEl equilibrio está en dar el paso cuando estás listo, no cuando te desesperás.\n\nSeguinos para más.",
    ],
    "Qué hace una consultora de RRHH y cómo te ayuda": [
        "Una consultora de RRHH como la nuestra conecta a las empresas con las personas correctas. Sin costo para el candidato.\n\nTe ayudamos a preparar el CV, te preparamos para la entrevista y te presentamos al empleador.\n\nMandanos tu CV por DM.",
        "¿Para qué sirve una consultora? Para que no busques trabajo solo.\n\nNosotros conocemos las empresas que están contratando, lo que buscan y cómo entrar.\n\nMandanos tu CV por DM y empezamos.",
        "El servicio de una consultora de RRHH para candidatos es 100% gratuito.\n\nLas empresas pagan por encontrar al candidato correcto. Vos solo traés las ganas.\n\nMandanos tu CV por DM.",
        "No solo te conseguimos entrevistas. Te preparamos para ellas.\n\nOrientación, feedback de CV y acompañamiento en todo el proceso. Sin costo para vos.\n\nMandanos un DM.",
    ],
    "Sectores industriales: Loma Negra, Cemento Avellaneda": [
        "Loma Negra y Cemento Avellaneda son dos de los mayores empleadores de Olavarría.\n\nBuscan operarios, técnicos, personal de mantenimiento y administración de forma constante.\n\nMandanos tu CV por DM si querés postularte.",
        "La industria cementera de Olavarría emplea a miles de personas en la región.\n\nY siempre hay búsquedas activas. ¿Tenés perfil técnico o industrial? Esto es para vos.\n\nMandanos tu CV por DM.",
        "¿Conocés todas las empresas industriales que operan en Olavarría? Más allá del cemento, hay metalúrgicas, talleres y servicios que contratan todo el año.\n\nSeguinos para estar al tanto de las búsquedas.",
        "El sector industrial de Olavarría es uno de los más estables del país.\n\nSi buscás trabajo con continuidad y posibilidades de crecimiento, es donde tenés que estar.\n\nMandanos tu CV por DM.",
    ],
    "Reflexión o quote sobre empleo": [
        "'El éxito no es la clave de la felicidad. La felicidad es la clave del éxito.' — Albert Schweitzer\n\nElegí bien dónde ponés tu energía laboral.\n\nSeguinos para más reflexiones.",
        "Trabajar para vivir o vivir para trabajar. La diferencia está en el trabajo que elegís.\n\nEncontrá uno que te deje tiempo para las dos cosas.\n\nSeguinos para más tips laborales.",
        "No subestimes el poder de hacer bien lo básico.\n\nLlegar a horario, cumplir lo que prometés, comunicar cuando algo sale mal. Eso construye reputación.\n\nSeguinos para más.",
        "El mejor momento para actualizar el CV es cuando tenés trabajo.\n\nNo esperes a necesitarlo. Tenerlo listo te da ventaja.\n\nSeguinos para más tips.",
    ],
    "Tip para el primer día en un trabajo nuevo": [
        "Primer día en un trabajo nuevo: llegá temprano, presentate con todos, escuchá más de lo que hablás.\n\nNo vengas a demostrar nada. Venís a aprender cómo funciona esto.\n\nSeguinos para más tips laborales.",
        "En el primer mes no es necesario tener todas las respuestas. Sí es necesario hacer buenas preguntas.\n\nMostrá disposición, anotá todo y pedí feedback temprano.\n\nSeguinos para más.",
        "El primer día marca la primera impresión. Vestite acorde, apagá el teléfono en reuniones y usá el nombre de cada persona.\n\nCosas simples que dicen mucho.\n\nSeguinos para más tips.",
        "Adaptarse a un nuevo trabajo lleva tiempo. No te presiones por ser perfecto desde el día uno.\n\nFocate en entender la cultura, el equipo y los procesos. Lo demás viene solo.\n\nSeguinos para más.",
    ],
    "Pasos para postularse: proceso simple": [
        "¿Cómo postularte a través de nuestra consultora?\n\n1. Mandanos tu CV por DM\n2. Conversamos sobre tu perfil y lo que buscás\n3. Te presentamos a las búsquedas que encajan\n\nAsí de simple. Y sin costo.",
        "El proceso es fácil:\n\n1. CV actualizado → lo revisamos juntos\n2. Te contamos las búsquedas activas\n3. Si hay match, te preparamos para la entrevista\n\nMandanos tu CV por DM y empezamos hoy.",
        "Para postularte no necesitás título universitario ni experiencia de años.\n\nNecesitás un CV honesto y ganas de trabajar.\n\nMandanos el tuyo por DM.",
        "Postularse por primera vez puede dar miedo. Pero el proceso con nosotros es simple y sin presión.\n\nMandanos tu CV por DM y te acompañamos desde el principio.",
    ],
    "CTA: mandanos tu CV": [
        "Si estás buscando trabajo en Olavarría, este es el momento.\n\nTenemos búsquedas activas en industria, logística y administración.\n\nMandanos tu CV por DM ahora.",
        "No esperes a que el trabajo ideal aparezca solo. Poné el CV en movimiento.\n\nMandanos tu perfil por DM y nosotros lo ponemos donde tiene que estar.",
        "¿Tu CV lleva meses sin movimiento? Tiempo de cambiar eso.\n\nMandanos el tuyo por DM y lo activamos.",
        "Una sola acción puede cambiar tu situación laboral: mandanos tu CV.\n\nSin costo, sin compromiso. Solo oportunidades.\n\nDM abierto.",
    ],
    "Dato del fin de semana: mercado laboral local": [
        "Dato del finde: Olavarría tiene más de 80.000 habitantes y una industria que emplea a una parte importante de la población activa.\n\nEl mercado local es chico pero activo.\n\nSeguinos para estar al tanto.",
        "¿Sabías que el sector servicios creció en Olavarría en los últimos años? Comercio, salud, educación y logística tienen búsquedas permanentes.\n\nSeguinos para más datos del mercado local.",
        "En Argentina, el 40% de los trabajos en zonas industriales se cubren por recomendación o consultora.\n\nEstar registrado en la nuestra te mete en ese 40%.\n\nMandanos tu CV por DM.",
        "El desempleo baja cuando los candidatos tienen herramientas: CV actualizado, orientación y acceso a búsquedas reales.\n\nNosotros te damos todo eso. Sin costo.\n\nMandanos tu perfil por DM.",
    ],
    "Motivacional fin de semana": [
        "El fin de semana también es tiempo para avanzar. Actualizá el CV, revisá LinkedIn, pensá qué querés.\n\n5 minutos de preparación hoy pueden abrirte una puerta la próxima semana.\n\nSeguinos.",
        "Descansá. Recargá. La búsqueda laboral también tiene sus tiempos.\n\nEl lunes arrancás con más energía si el finde lo usaste bien.\n\nSeguinos para más.",
        "Este finde, hacé una cosa por tu carrera. Una sola.\n\nActualizá el CV, mandalo a alguien, o simplemente leé sobre el sector que te interesa.\n\nPequenos pasos, grandes cambios. Seguinos.",
        "No se necesita un lunes para empezar. Se necesita una decisión.\n\nHoy es tan buen día como cualquier otro para dar el primer paso.\n\nMandanos tu CV por DM.",
    ],
    "Tip: cómo prepararse para la semana laboral": [
        "Antes del lunes:\n\n• Revisá si tenés entrevistas o seguimientos pendientes\n• Respondé mensajes de búsqueda sin responder\n• Prepará la ropa y el material si tenés algo agendado\n\nLlegar preparado hace toda la diferencia. Seguinos.",
        "La semana laboral arranca el domingo a la noche.\n\nRepasá tu agenda, tu lista de postulaciones activas y qué empresa tenés que seguir.\n\nSeguinos para más tips de organización.",
        "¿Tenés entrevista esta semana? Investigá la empresa hoy.\n\n15 minutos de investigación te dan confianza para las preguntas más difíciles.\n\nSeguinos para más tips.",
        "Empezar la semana con un objetivo claro cambia la productividad.\n\n'Esta semana voy a mandar 5 CVs y hacer 2 seguimientos' es mejor que 'voy a buscar trabajo'.\n\nSeguinos para más.",
    ],
    "Reflexión dominical sobre carrera y trabajo": [
        "Domingo de reflexión: ¿estás en el trabajo correcto, buscando el correcto, o en el camino correcto?\n\nLas tres son respuestas válidas. Lo importante es saberlo.\n\nSeguinos para acompañarte en el proceso.",
        "La carrera no es una línea recta. Tiene desvíos, pausas y arranques.\n\nLo que importa es que sigas avanzando en la dirección que elegiste.\n\nSeguinos para más reflexiones.",
        "¿Cuándo fue la última vez que te preguntaste si tu trabajo actual te acerca a donde querés estar?\n\nNo es una pregunta para angustiarse. Es para orientarse.\n\nSeguinos para más.",
        "El trabajo ideal no cae del cielo. Se construye con decisiones, paciencia y el apoyo correcto.\n\nEstamos acá para ser parte de ese proceso.\n\nSeguinos.",
    ],
    "Inspiracional: casos de crecimiento profesional": [
        "Hay personas que empezaron como operarios en Loma Negra y hoy lideran equipos de 20 personas.\n\nEl crecimiento existe. Requiere tiempo, actitud y el puesto correcto para empezar.\n\nMandanos tu CV por DM.",
        "Crecimiento real: entrar como auxiliar administrativo y en 3 años estar a cargo del área.\n\nPasa en Olavarría. Pasa cuando entrás por el lugar correcto.\n\nMandanos tu perfil por DM.",
        "No siempre el primer trabajo es el que querías. Pero puede ser el que abre todas las puertas siguientes.\n\nEntrá, aprendé, crecé.\n\nMandanos tu CV por DM.",
        "Casos reales de nuestra consultora: candidatos que encontraron trabajo en menos de 2 semanas.\n\nPorque el CV estaba bien, la búsqueda encajaba y el proceso fue rápido.\n\nMandanos el tuyo por DM.",
    ],
    "Preview de la semana: qué viene": [
        "Esta semana arranca con búsquedas activas en industria y administración.\n\nSi tu CV está listo, este es el momento.\n\nMandanos el tuyo por DM y te sumamos a los procesos.",
        "Nueva semana, nuevas búsquedas.\n\nSeguinos esta semana para ver los perfiles que buscan las empresas de Olavarría.\n\nY mandanos tu CV por DM si querés postularte.",
        "Esta semana publicamos los perfiles más buscados de junio.\n\nSeguinos para no perderte nada y mandanos tu CV por DM si estás disponible.",
        "Semana nueva. ¿Qué cambió en tu búsqueda?\n\nSi querés arrancar distinto, empezá por actualizá el CV y mandárnoslo por DM.",
    ],
}

import random

def generate_caption(content_type: str, post_number: int) -> str:
    # Find best matching template key
    key = content_type
    if key not in CAPTION_TEMPLATES:
        # Fuzzy match
        for k in CAPTION_TEMPLATES:
            if any(w in content_type.lower() for w in k.lower().split()[:3]):
                key = k; break
    options = CAPTION_TEMPLATES.get(key, [f"{content_type}\n\nMandanos tu CV por DM."])
    return options[(post_number - 1) % len(options)]


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

            media_url = pick_media(content_type, post_number)
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
