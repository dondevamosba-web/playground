"""
Generates the complete OLA Digital static website.
Outputs: website/index.html, website/assets/logo.svg,
         website/assets/favicon.svg, website/assets/css/custom.css
Usage: python tools/generate_website.py
"""

import os
from pathlib import Path

BRAND = {
    "name": "OLA Digital",
    "tagline": "Hacemos crecer negocios en Olavarría.",
    "subheadline": "Agencia de marketing digital en Olavarría — ayudamos a negocios locales a crecer en internet.",
    "email": "hola@oladigital.com.ar",
    "whatsapp_number": "5491162310105",
    "whatsapp_display": "+54 9 11 6231-0105",
    "whatsapp_message": "Hola%2C%20me%20gustar%C3%ADa%20consultar%20sobre%20sus%20servicios.",
    "color_primary": "#0EA5E9",
    "color_primary_dark": "#0284C7",
    "color_accent": "#F97316",
    "color_dark": "#0F172A",
    "color_mid": "#475569",
    "color_light": "#F0F9FF",
    "color_white": "#FFFFFF",
    "city": "Olavarría",
    "province": "Buenos Aires",
    "country": "Argentina",
}

SERVICES = [
    {
        "title": "Redes Sociales",
        "description": "Gestionamos tu Instagram, Facebook y TikTok con contenido que conecta con tu comunidad y convierte seguidores en clientes.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>',
    },
    {
        "title": "SEO Local",
        "description": "Aparecer primero en Google cuando tus clientes buscan en Olavarría. Más visibilidad, más llamados, más ventas.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>',
    },
    {
        "title": "Google Ads",
        "description": "Campañas de pago por clic con presupuestos adaptados a negocios locales. Pagás solo cuando alguien hace clic.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/>',
    },
    {
        "title": "Diseño Web",
        "description": "Sitios modernos, rápidos y optimizados para móvil. Tu página es tu vendedor 24/7 — hacemos que trabaje bien.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>',
    },
    {
        "title": "Contenido",
        "description": "Textos, fotos y videos que cuentan tu historia y atraen clientes. Contenido que posiciona y que la gente comparte.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>',
    },
    {
        "title": "Email Marketing",
        "description": "Newsletters y automatizaciones que mantienen tu marca presente y traen clientes de vuelta cuando más los necesitás.",
        "icon": '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>',
    },
]

PROCESS_STEPS = [
    ("01", "Diagnóstico gratuito", "Analizamos tu presencia digital actual y la de tu competencia en Olavarría."),
    ("02", "Estrategia a medida", "Diseñamos un plan específico para tu negocio, tu presupuesto y tus objetivos."),
    ("03", "Ejecución y optimización", "Implementamos, medimos y ajustamos semana a semana para maximizar resultados."),
    ("04", "Reportes claros", "Cada mes recibís un informe simple que muestra exactamente qué logramos juntos."),
]

OWNER = {
    "name": "Guido Carminatti",
    "role": "Fundador & Director, OLA Digital",
    "photo_url": "https://media.licdn.com/dms/image/v2/D4D35AQF7ESb05deNeA/profile-framedphoto-shrink_800_800/profile-framedphoto-shrink_800_800/0/1705868515569?e=1779807600&v=beta&t=ysaBPCyjysKj9xZeKHAUUECOhNd_uTgqUrP5-E4RIow",
    "bio": (
        "Soy Guido, fundador de OLA Digital. Nací y crecí en Olavarría, y vi de primera mano cómo los negocios locales perdían clientes "
        "frente a competidores que simplemente tenían mejor presencia digital.<br/><br/>"
        "Creé OLA Digital para resolver ese problema: traer marketing digital de calidad directamente a los negocios de la ciudad, "
        "sin precios de agencia porteña ni resultados genéricos. Cada cliente es un vecino — eso cambia cómo trabajamos."
    ),
}

TESTIMONIALS = [
    {
        "quote": "OLA Digital transformó nuestra presencia en Instagram. Pasamos de postear cuando podíamos a tener una comunidad cervecera activa que comparte, comenta y viene al local.",
        "name": "Sur del Sur",
        "business": "Compañía Cervecera · Olavarría",
        "instagram": "https://www.instagram.com/sur.del.sur/",
        "handle": "@sur.del.sur",
        "service": "Redes Sociales",
        "color": "#1a1a2e",
    },
    {
        "quote": "Desde que OLA nos ayudó con la estrategia digital, las reservas online crecieron un montón. Hoy llegan clientes nuevos que nos encontraron en Instagram antes de venir a comer.",
        "name": "Pietra",
        "business": "Restaurante · Olavarría",
        "instagram": "https://www.instagram.com/pietraolavarria/",
        "handle": "@pietraolavarria",
        "service": "Redes Sociales + Reservas",
        "color": "#8B4513",
    },
    {
        "quote": "Nos diseñaron la tienda online desde cero y nos ayudaron a llegar a clientes en todo el país. Hoy vendemos mapas de Buenos Aires a Ushuaia gracias al trabajo de OLA.",
        "name": "Maroni Maps",
        "business": "Tienda de Mapas · Argentina",
        "instagram": "https://maronimaps.com/",
        "handle": "maronimaps.com",
        "service": "Diseño Web + E-commerce",
        "color": "#2563EB",
    },
]

PORTFOLIO = [
    {
        "client": "Sur del Sur",
        "category": "Cervecería Artesanal",
        "tags": ["Redes Sociales", "Contenido", "Comunidad"],
        "description": "Gestión integral de Instagram para la cervecería artesanal de Olavarría. Estrategia de contenido, fotografía de producto y comunidad.",
        "result": "+280% alcance orgánico en 4 meses",
        "link": "https://www.instagram.com/sur.del.sur/",
        "link_label": "@sur.del.sur",
        "color_bg": "#18120a",
        "color_accent": "#d97706",
        "color_accent2": "#f59e0b",
        "display": "stat",
        "stat_number": "+280%",
        "stat_label": "alcance orgánico\nen Instagram",
        "stat_sub": "en 4 meses",
        "icon": "🍺",
        "pattern_color": "#d97706",
    },
    {
        "client": "Pietra",
        "category": "Restaurante",
        "tags": ["Redes Sociales", "Reservas Online", "Gastronomía"],
        "description": "Estrategia digital y sistema de reservas para el restaurante. Contenido gastronómico que convierte seguidores en comensales.",
        "result": "Reservas online activas · 3× más consultas",
        "link": "https://www.instagram.com/pietraolavarria/",
        "link_label": "@pietraolavarria",
        "color_bg": "#1c0d04",
        "color_accent": "#ea580c",
        "color_accent2": "#fb923c",
        "display": "stat",
        "stat_number": "3×",
        "stat_label": "más consultas\ny reservas",
        "stat_sub": "en 3 meses",
        "icon": "🍽️",
        "pattern_color": "#ea580c",
    },
    {
        "client": "Maroni Maps",
        "category": "E-commerce",
        "tags": ["Diseño Web", "Tienda Online", "Marketing Digital"],
        "description": "Diseño y lanzamiento de tienda online para venta de mapas de relieve de Argentina. Alcance nacional desde Olavarría.",
        "result": "Tienda activa · envíos a todo el país",
        "link": "https://maronimaps.com/",
        "link_label": "maronimaps.com",
        "color_bg": "#0c1628",
        "color_accent": "#38bdf8",
        "color_accent2": "#7dd3fc",
        "display": "website",
        "photo_url": "https://acdn-us.mitiendanube.com/stores/007/046/685/products/hero-image-f25279ee0744af603517691086757512-480-0.webp",
        "logo_url": "http://acdn-us.mitiendanube.com/stores/007/046/685/themes/common/logo-1991807338-1769091459-467601d19e774efa52c36ec4f5bed1821769091459.png?0",
    },
]


def build_logo_svg(brand, dark_bg=False):
    """Full horizontal wordmark: wave-badge + OLA + Digital.
    dark_bg=True renders text in white (for use on dark backgrounds).
    """
    ola_fill    = "url(#olaGrad)"
    digit_fill  = "#FFFFFF" if dark_bg else "#334155"
    badge_bg    = "url(#badgeGrad)"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 248 64" fill="none">
  <defs>
    <!-- Badge gradient: deep ocean → sky -->
    <linearGradient id="badgeGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0369A1"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>
    <!-- OLA text gradient: ocean left → cyan right -->
    <linearGradient id="olaGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#0C4A6E"/>
      <stop offset="100%" stop-color="#0EA5E9"/>
    </linearGradient>
  </defs>

  <!-- Wave mark badge -->
  <rect x="0" y="4" width="56" height="56" rx="14" fill="{badge_bg}"/>
  <!-- 3 sinusoidal waves (cubic bezier) inside badge -->
  <path d="M8,20 C13,15 17,15 22,20 C27,25 31,25 36,20 C41,15 45,15 50,20"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.45"/>
  <path d="M8,32 C13,27 17,27 22,32 C27,37 31,37 36,32 C41,27 45,27 50,32"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.72"/>
  <path d="M8,44 C13,39 17,39 22,44 C27,49 31,49 36,44 C41,39 45,39 50,44"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none"/>

  <!-- OLA -->
  <text x="68" y="42"
        font-family="Plus Jakarta Sans, Arial Black, sans-serif"
        font-weight="800" font-size="38"
        fill="{ola_fill}">OLA</text>

  <!-- DIGITAL – spaced small caps feel -->
  <text x="70" y="57"
        font-family="Inter, Arial, sans-serif"
        font-weight="600" font-size="12"
        letter-spacing="4"
        fill="{digit_fill}">DIGITAL</text>
</svg>'''


def build_logo_white_svg(brand):
    """White version for dark backgrounds (nav, footer, dark cards)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 248 64" fill="none">
  <defs>
    <linearGradient id="badgeGradW" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.30)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0.12)"/>
    </linearGradient>
  </defs>
  <rect x="0" y="4" width="56" height="56" rx="14" fill="url(#badgeGradW)" stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
  <path d="M8,20 C13,15 17,15 22,20 C27,25 31,25 36,20 C41,15 45,15 50,20"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.45"/>
  <path d="M8,32 C13,27 17,27 22,32 C27,37 31,37 36,32 C41,27 45,27 50,32"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none" opacity="0.72"/>
  <path d="M8,44 C13,39 17,39 22,44 C27,49 31,49 36,44 C41,39 45,39 50,44"
        stroke="white" stroke-width="2.2" stroke-linecap="round" fill="none"/>
  <text x="68" y="42"
        font-family="Plus Jakarta Sans, Arial Black, sans-serif"
        font-weight="800" font-size="38" fill="white">OLA</text>
  <text x="70" y="57"
        font-family="Inter, Arial, sans-serif"
        font-weight="600" font-size="12"
        letter-spacing="4" fill="rgba(255,255,255,0.70)">DIGITAL</text>
</svg>'''


def build_logo_icon_svg(brand):
    """Square wave-mark icon — use as app icon, WhatsApp profile pic, favicon source."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <defs>
    <linearGradient id="iconGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0EA5E9"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="16" fill="url(#iconGrad)"/>
  <!-- 3 waves, vertically centred in 64×64 -->
  <path d="M10,22 C17,16 23,16 30,22 C37,28 43,28 54,22"
        stroke="white" stroke-width="2.8" stroke-linecap="round" fill="none" opacity="0.45"/>
  <path d="M10,32 C17,26 23,26 30,32 C37,38 43,38 54,32"
        stroke="white" stroke-width="2.8" stroke-linecap="round" fill="none" opacity="0.72"/>
  <path d="M10,42 C17,36 23,36 30,42 C37,48 43,48 54,42"
        stroke="white" stroke-width="2.8" stroke-linecap="round" fill="none"/>
</svg>'''


def build_favicon_svg(brand):
    """16–32 px favicon — simplified 2-wave mark."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="fvGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0EA5E9"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="8" fill="url(#fvGrad)"/>
  <path d="M5,13 C9,9 13,9 16,13 C19,17 23,17 27,13"
        stroke="white" stroke-width="2.5" stroke-linecap="round" fill="none" opacity="0.6"/>
  <path d="M5,21 C9,17 13,17 16,21 C19,25 23,25 27,21"
        stroke="white" stroke-width="2.5" stroke-linecap="round" fill="none"/>
</svg>'''


def build_custom_css(brand):
    return f'''/* OLA Digital — custom styles */

html {{
  scroll-behavior: smooth;
}}

::-webkit-scrollbar {{
  width: 6px;
}}
::-webkit-scrollbar-track {{
  background: {brand['color_light']};
}}
::-webkit-scrollbar-thumb {{
  background: {brand['color_primary']};
  border-radius: 3px;
}}

/* WhatsApp pulse ring */
@keyframes pulse-ring {{
  0% {{ transform: scale(1); opacity: 0.6; }}
  100% {{ transform: scale(1.6); opacity: 0; }}
}}
.whatsapp-pulse::before {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: #25D366;
  animation: pulse-ring 2s ease-out infinite;
  z-index: -1;
}}

/* Fade-in on scroll */
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(24px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-fadeInUp {{
  animation: fadeInUp 0.6s ease-out forwards;
}}

/* Nav glass on scroll — toggled by JS */
.nav-scrolled {{
  background: rgba(255,255,255,0.92) !important;
  backdrop-filter: blur(12px);
  box-shadow: 0 1px 0 rgba(0,0,0,0.08);
}}

/* Gradient hero bg */
.hero-bg {{
  background: radial-gradient(ellipse 80% 60% at 60% 40%, rgba(14,165,233,0.08) 0%, transparent 70%),
              radial-gradient(ellipse 40% 40% at 90% 80%, rgba(249,115,22,0.05) 0%, transparent 60%);
}}

/* Step connector line */
.step-line {{
  position: absolute;
  top: 20px;
  left: calc(50% + 20px);
  right: calc(-50% + 20px);
  height: 2px;
  background: linear-gradient(90deg, {brand['color_primary']}40, {brand['color_primary']}20);
}}

/* Card hover */
.service-card {{
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.service-card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(14,165,233,0.12);
}}

/* Portfolio slider */
.portfolio-track {{
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 1rem;
}}
.portfolio-track::-webkit-scrollbar {{
  display: none;
}}
.portfolio-card {{
  scroll-snap-align: start;
  flex: 0 0 340px;
  min-width: 340px;
}}
@media (max-width: 640px) {{
  .portfolio-card {{
    flex: 0 0 290px;
    min-width: 290px;
  }}
}}

/* Testimonial card */
.testimonial-card {{
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.testimonial-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 16px 40px rgba(14,165,233,0.10);
}}
'''


def build_head(brand):
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>OLA Digital | Agencia de Marketing Digital en Olavarría</title>
  <meta name="description" content="Agencia de marketing digital en Olavarría, Buenos Aires. Redes sociales, SEO local, Google Ads y diseño web para negocios locales. Consultá gratis."/>
  <meta name="keywords" content="marketing digital Olavarría, agencia digital Olavarría, SEO Olavarría, redes sociales Olavarría, Google Ads Buenos Aires"/>
  <link rel="canonical" href="https://oladigital.com.ar/"/>

  <!-- Open Graph -->
  <meta property="og:type" content="website"/>
  <meta property="og:url" content="https://oladigital.com.ar/"/>
  <meta property="og:title" content="OLA Digital — Marketing Digital en Olavarría"/>
  <meta property="og:description" content="Hacemos crecer negocios locales en internet. Redes sociales, SEO, Google Ads y más."/>
  <meta property="og:image" content="https://oladigital.com.ar/assets/og-image.png"/>
  <meta name="twitter:card" content="summary_large_image"/>

  <!-- Schema.org LocalBusiness -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "MarketingAgency",
    "name": "OLA Digital",
    "description": "Agencia de marketing digital en Olavarría, Buenos Aires.",
    "url": "https://oladigital.com.ar",
    "telephone": "+54-9-11-6231-0105",
    "email": "hola@oladigital.com.ar",
    "address": {{
      "@type": "PostalAddress",
      "addressLocality": "Olavarría",
      "addressRegion": "Buenos Aires",
      "addressCountry": "AR"
    }},
    "areaServed": {{
      "@type": "City",
      "name": "Olavarría"
    }}
  }}
  </script>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>

  <!-- Tailwind CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'brand-blue':       '{brand["color_primary"]}',
            'brand-blue-dark':  '{brand["color_primary_dark"]}',
            'brand-orange':     '{brand["color_accent"]}',
            'brand-dark':       '{brand["color_dark"]}',
            'brand-mid':        '{brand["color_mid"]}',
            'brand-light':      '{brand["color_light"]}',
          }},
          fontFamily: {{
            heading: ['Plus Jakarta Sans', 'sans-serif'],
            body:    ['Inter', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>

  <link rel="stylesheet" href="assets/css/custom.css"/>
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg"/>
</head>'''


def build_nav(brand):
    nav_links = [
        ("#servicios", "Servicios"),
        ("#trabajos", "Trabajos"),
        ("#nosotros", "Nosotros"),
        ("#contacto", "Contacto"),
    ]
    links_html = "\n".join(
        f'          <a href="{href}" class="text-brand-mid hover:text-brand-blue font-body font-medium text-sm transition-colors">{label}</a>'
        for href, label in nav_links
    )
    return f'''
<nav id="navbar" class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 py-4 px-6 lg:px-16">
  <div class="max-w-6xl mx-auto flex items-center justify-between">
    <!-- Logo: colour on white, switches to white version on dark scroll bg -->
    <a href="#" class="flex-shrink-0">
      <img id="nav-logo" src="assets/logo.svg" alt="OLA Digital" class="h-9 w-auto"/>
    </a>

    <!-- Desktop nav -->
    <div class="hidden md:flex items-center gap-8">
{links_html}
      <a href="#contacto" class="bg-brand-blue hover:bg-brand-blue-dark text-white font-body font-semibold text-sm px-5 py-2.5 rounded-full transition-colors">
        Hablemos
      </a>
    </div>

    <!-- Mobile hamburger -->
    <div class="md:hidden">
      <input type="checkbox" id="menu-toggle" class="hidden peer"/>
      <label for="menu-toggle" class="cursor-pointer flex flex-col gap-1.5 p-1">
        <span class="block w-6 h-0.5 bg-brand-dark transition-all peer-checked:rotate-45"></span>
        <span class="block w-6 h-0.5 bg-brand-dark"></span>
        <span class="block w-6 h-0.5 bg-brand-dark"></span>
      </label>
      <div class="peer-checked:flex hidden absolute top-full left-0 right-0 bg-white shadow-lg flex-col items-center gap-6 py-8">
        {''.join(f'<a href="{href}" class="text-brand-dark font-body font-medium text-base">{label}</a>' for href, label in nav_links)}
        <a href="#contacto" class="bg-brand-blue text-white font-semibold text-sm px-6 py-3 rounded-full">Hablemos</a>
      </div>
    </div>
  </div>
</nav>

<script>
  const navbar  = document.getElementById('navbar');
  const navLogo = document.getElementById('nav-logo');
  window.addEventListener('scroll', () => {{
    if (window.scrollY > 20) {{
      navbar.classList.add('nav-scrolled');
      navLogo.src = 'assets/logo.svg';
    }} else {{
      navbar.classList.remove('nav-scrolled');
      navLogo.src = 'assets/logo.svg';
    }}
  }});
</script>'''


def build_hero(brand):
    hero_svg = f'''<svg viewBox="0 0 480 400" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full max-w-lg">
  <!-- Background circles -->
  <circle cx="240" cy="200" r="160" fill="{brand['color_primary']}" opacity="0.06"/>
  <circle cx="240" cy="200" r="110" fill="{brand['color_primary']}" opacity="0.06"/>
  <!-- Phone mockup -->
  <rect x="170" y="80" width="140" height="240" rx="20" fill="white" stroke="{brand['color_primary']}" stroke-width="3"/>
  <rect x="185" y="100" width="110" height="180" rx="4" fill="{brand['color_light']}"/>
  <!-- Screen content bars -->
  <rect x="195" y="115" width="90" height="10" rx="5" fill="{brand['color_primary']}" opacity="0.3"/>
  <rect x="195" y="133" width="65" height="8" rx="4" fill="{brand['color_mid']}" opacity="0.25"/>
  <rect x="195" y="150" width="90" height="45" rx="8" fill="{brand['color_primary']}" opacity="0.12"/>
  <rect x="195" y="204" width="42" height="42" rx="8" fill="{brand['color_accent']}" opacity="0.15"/>
  <rect x="243" y="204" width="42" height="42" rx="8" fill="{brand['color_primary']}" opacity="0.15"/>
  <rect x="195" y="252" width="90" height="8" rx="4" fill="{brand['color_mid']}" opacity="0.2"/>
  <!-- Home indicator -->
  <rect x="215" y="300" width="50" height="4" rx="2" fill="{brand['color_mid']}" opacity="0.3"/>
  <!-- Floating badges -->
  <g transform="translate(60, 120)">
    <rect width="110" height="44" rx="12" fill="white" filter="url(#shadow)"/>
    <circle cx="22" cy="22" r="14" fill="{brand['color_primary']}" opacity="0.15"/>
    <text x="22" y="27" text-anchor="middle" font-size="14">📈</text>
    <rect x="44" y="14" width="52" height="7" rx="3.5" fill="{brand['color_dark']}" opacity="0.15"/>
    <rect x="44" y="26" width="36" height="6" rx="3" fill="{brand['color_primary']}" opacity="0.25"/>
  </g>
  <g transform="translate(310, 230)">
    <rect width="110" height="44" rx="12" fill="white" filter="url(#shadow)"/>
    <circle cx="22" cy="22" r="14" fill="{brand['color_accent']}" opacity="0.15"/>
    <text x="22" y="27" text-anchor="middle" font-size="14">⭐</text>
    <rect x="44" y="14" width="52" height="7" rx="3.5" fill="{brand['color_dark']}" opacity="0.15"/>
    <rect x="44" y="26" width="40" height="6" rx="3" fill="{brand['color_accent']}" opacity="0.25"/>
  </g>
  <!-- Connecting lines -->
  <line x1="170" y1="160" x2="120" y2="142" stroke="{brand['color_primary']}" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.4"/>
  <line x1="310" y1="250" x2="365" y2="252" stroke="{brand['color_accent']}" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.4"/>
  <!-- Dots -->
  <circle cx="380" cy="120" r="6" fill="{brand['color_primary']}" opacity="0.3"/>
  <circle cx="90" cy="300" r="8" fill="{brand['color_accent']}" opacity="0.2"/>
  <circle cx="420" cy="300" r="5" fill="{brand['color_primary']}" opacity="0.25"/>
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="{brand['color_primary']}" flood-opacity="0.12"/>
    </filter>
  </defs>
</svg>'''

    return f'''
<section class="hero-bg min-h-screen flex items-center pt-20 pb-16 px-6 lg:px-16">
  <div class="max-w-6xl mx-auto w-full grid md:grid-cols-2 gap-12 items-center">
    <!-- Text -->
    <div class="order-2 md:order-1">
      <div class="inline-flex items-center gap-2 bg-brand-blue/10 text-brand-blue font-body font-semibold text-sm px-4 py-1.5 rounded-full mb-6">
        <span class="w-2 h-2 bg-brand-blue rounded-full animate-pulse"></span>
        Agencia local en Olavarría
      </div>
      <h1 class="font-heading font-extrabold text-4xl lg:text-5xl xl:text-6xl text-brand-dark leading-tight mb-6">
        Hacemos crecer<br/>
        <span class="text-brand-blue">negocios locales</span><br/>
        en internet.
      </h1>
      <p class="font-body text-brand-mid text-lg leading-relaxed mb-8 max-w-lg">
        Somos la agencia de marketing digital de Olavarría. Conocemos el mercado local y sabemos cómo conectar tu negocio con los clientes de la ciudad.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <a href="#servicios" class="inline-flex items-center justify-center gap-2 bg-brand-blue hover:bg-brand-blue-dark text-white font-body font-semibold px-7 py-3.5 rounded-full transition-colors text-base">
          Ver servicios
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
        </a>
        <a href="https://wa.me/{brand['whatsapp_number']}?text={brand['whatsapp_message']}" target="_blank" rel="noopener"
           class="inline-flex items-center justify-center gap-2 bg-[#25D366] hover:bg-[#1ebe5a] text-white font-body font-semibold px-7 py-3.5 rounded-full transition-colors text-base">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.126.553 4.122 1.524 5.854L0 24l6.335-1.502A11.954 11.954 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.493-5.18-1.357l-.37-.219-3.835.909.971-3.75-.241-.385A9.937 9.937 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
          Escribinos por WhatsApp
        </a>
      </div>
      <div class="flex items-center gap-8 mt-10 pt-8 border-t border-gray-100">
        <div>
          <div class="font-heading font-bold text-2xl text-brand-dark">+50</div>
          <div class="font-body text-brand-mid text-sm">Clientes activos</div>
        </div>
        <div class="w-px h-10 bg-gray-200"></div>
        <div>
          <div class="font-heading font-bold text-2xl text-brand-dark">3 años</div>
          <div class="font-body text-brand-mid text-sm">En Olavarría</div>
        </div>
        <div class="w-px h-10 bg-gray-200"></div>
        <div>
          <div class="font-heading font-bold text-2xl text-brand-dark">100%</div>
          <div class="font-body text-brand-mid text-sm">Local</div>
        </div>
      </div>
    </div>
    <!-- Illustration -->
    <div class="order-1 md:order-2 flex justify-center">
      {hero_svg}
    </div>
  </div>
</section>'''


def build_services(brand):
    cards = ""
    for svc in SERVICES:
        cards += f'''
      <div class="service-card bg-white rounded-2xl p-7 border border-gray-100">
        <div class="w-12 h-12 bg-brand-blue/10 rounded-xl flex items-center justify-center mb-5">
          <svg class="w-6 h-6 text-brand-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {svc["icon"]}
          </svg>
        </div>
        <h3 class="font-heading font-bold text-lg text-brand-dark mb-2">{svc["title"]}</h3>
        <p class="font-body text-brand-mid text-sm leading-relaxed">{svc["description"]}</p>
      </div>'''

    return f'''
<section id="servicios" class="py-20 px-6 lg:px-16 bg-white">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14">
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Nuestros servicios</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-4">Todo lo que tu negocio necesita<br/>para crecer online</h2>
      <p class="font-body text-brand-mid text-lg max-w-2xl mx-auto">Desde redes sociales hasta posicionamiento en Google — trabajamos con cada herramienta digital para que más personas encuentren y elijan tu negocio.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {cards}
    </div>
    <div class="mt-12 text-center">
      <a href="#contacto" class="inline-flex items-center gap-2 bg-brand-orange hover:bg-orange-600 text-white font-body font-semibold px-8 py-3.5 rounded-full transition-colors">
        Consultá gratis qué servicio necesitás
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
      </a>
    </div>
  </div>
</section>'''


def build_local(brand):
    stats = [
        ("12.000+", "negocios activos en el partido de Olavarría"),
        ("+340%", "crecimiento en búsquedas 'cerca de mí' en los últimos 3 años"),
        ("1 de cada 2", "compras locales empieza con una búsqueda en Google"),
    ]
    stats_html = ""
    for value, label in stats:
        stats_html += f'''
        <div class="bg-white rounded-2xl p-6 border border-brand-blue/10 text-center">
          <div class="font-heading font-extrabold text-3xl text-brand-blue mb-2">{value}</div>
          <div class="font-body text-brand-mid text-sm leading-snug">{label}</div>
        </div>'''

    return f'''
<section id="local" class="py-20 px-6 lg:px-16 bg-brand-light">
  <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
    <div>
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Por qué una agencia local</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-6">Conocemos Olavarría.<br/>Eso importa.</h2>
      <div class="space-y-4 font-body text-brand-mid text-base leading-relaxed">
        <p>No somos una agencia de Buenos Aires que te manda un reporte por email. Somos de acá. Sabemos que el viernes hay partido en el Fortín, que la industria cementera mueve la economía local, y que el comercio de calle Rivadavia tiene dinámicas propias.</p>
        <p>Eso nos permite hacer campañas que realmente resuenan con la gente de Olavarría, no mensajes genéricos que funcionan para cualquier ciudad del país.</p>
        <p>Cuando tu negocio crece, nosotros crecemos. Esa alineación de intereses es lo que hace que nuestros clientes trabajen con nosotros por años, no por meses.</p>
      </div>
      <a href="#contacto" class="inline-flex items-center gap-2 mt-8 text-brand-blue font-body font-semibold hover:underline">
        Contanos tu negocio
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
      </a>
    </div>
    <div class="grid gap-4">
      {stats_html}
    </div>
  </div>
</section>'''


def build_process(brand):
    steps_html = ""
    for i, (num, title, desc) in enumerate(PROCESS_STEPS):
        connector = '<div class="step-line hidden lg:block"></div>' if i < len(PROCESS_STEPS) - 1 else ''
        steps_html += f'''
      <div class="relative flex flex-col items-center text-center">
        <div class="w-12 h-12 rounded-full bg-brand-blue flex items-center justify-center text-white font-heading font-bold text-base mb-4 relative z-10">{num}</div>
        {connector}
        <h3 class="font-heading font-bold text-base text-brand-dark mb-2">{title}</h3>
        <p class="font-body text-brand-mid text-sm leading-relaxed">{desc}</p>
      </div>'''

    return f'''
<section class="py-20 px-6 lg:px-16 bg-white">
  <div class="max-w-5xl mx-auto">
    <div class="text-center mb-14">
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Cómo trabajamos</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-4">Simple, transparente, efectivo</h2>
      <p class="font-body text-brand-mid text-lg max-w-xl mx-auto">Sin contratos eternos ni lenguaje técnico. Un proceso claro de cuatro pasos para que veas resultados desde el primer mes.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
      {steps_html}
    </div>
  </div>
</section>'''


def build_testimonials(brand):
    cards_html = ""
    for t in TESTIMONIALS:
        instagram_icon = '<svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>'
        link_icon = '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>'
        is_web = t["handle"].endswith(".com")
        link_icon_html = link_icon if is_web else instagram_icon
        cards_html += f'''
      <div class="testimonial-card bg-white rounded-2xl p-7 border border-gray-100 flex flex-col gap-5">
        <div class="flex items-center justify-between">
          <div class="flex gap-0.5">
            {''.join(['<span class="text-brand-orange">★</span>' for _ in range(5)])}
          </div>
          <span class="font-body text-xs font-semibold text-brand-blue bg-brand-blue/10 px-3 py-1 rounded-full">{t["service"]}</span>
        </div>
        <p class="font-body text-brand-dark text-base leading-relaxed flex-1 italic">"{t["quote"]}"</p>
        <div class="flex items-center justify-between pt-2 border-t border-gray-50">
          <div>
            <div class="font-heading font-bold text-brand-dark text-sm">{t["name"]}</div>
            <div class="font-body text-brand-mid text-xs mt-0.5">{t["business"]}</div>
          </div>
          <a href="{t["instagram"]}" target="_blank" rel="noopener"
             class="flex items-center gap-1.5 text-brand-mid hover:text-brand-blue text-xs font-body font-medium transition-colors">
            {link_icon_html}
            {t["handle"]}
          </a>
        </div>
      </div>'''

    return f'''
<section id="testimonios" class="py-20 px-6 lg:px-16 bg-brand-light">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14">
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Clientes reales</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-4">Negocios de Olavarría<br/>que ya crecen con OLA</h2>
      <p class="font-body text-brand-mid text-lg max-w-xl mx-auto">No son casos de éxito inventados. Son tus vecinos — comercios, restaurantes y marcas de la ciudad que apostaron al marketing digital.</p>
    </div>
    <div class="grid md:grid-cols-3 gap-6">
      {cards_html}
    </div>
  </div>
</section>'''


def build_about(brand):
    values = [
        ("Transparencia total", "Reportes claros cada mes. Siempre sabés en qué se invierte tu presupuesto y qué resultados estamos logrando."),
        ("Resultados medibles", "Sin métricas de vanidad: trabajamos sobre números que impactan directamente en tus ventas y tu negocio."),
        ("Comunicación directa", "Tenés acceso directo a quien trabaja tu cuenta. Sin intermediarios, sin demoras, sin sorpresas."),
    ]
    values_html = ""
    for title, desc in values:
        values_html += f'''
        <div class="flex gap-4">
          <div class="flex-shrink-0 w-8 h-8 rounded-full bg-brand-blue/10 flex items-center justify-center mt-0.5">
            <svg class="w-4 h-4 text-brand-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          </div>
          <div>
            <div class="font-body font-semibold text-brand-dark mb-1">{title}</div>
            <div class="font-body text-brand-mid text-sm leading-relaxed">{desc}</div>
          </div>
        </div>'''

    return f'''
<section id="nosotros" class="py-20 px-6 lg:px-16 bg-white">
  <div class="max-w-5xl mx-auto grid md:grid-cols-2 gap-14 items-center">
    <!-- Owner photo -->
    <div class="flex flex-col items-center md:items-start gap-5">
      <div class="relative">
        <div class="w-56 h-56 rounded-3xl overflow-hidden border-4 border-brand-blue/15 shadow-xl">
          <!-- scale(1.28) crops the LinkedIn "Open to Work" green ring frame -->
          <img src="{OWNER['photo_url']}"
               alt="{OWNER['name']}"
               class="w-full h-full object-cover object-center"
               style="transform:scale(1.28);transform-origin:center center;"
               loading="lazy"/>
        </div>
        <!-- Badge -->
        <div class="absolute -bottom-4 -right-4 bg-brand-blue text-white rounded-2xl px-4 py-2 shadow-lg">
          <div class="font-heading font-bold text-sm leading-tight">OLA Digital</div>
          <div class="font-body text-blue-100 text-xs">Olavarría, BA</div>
        </div>
      </div>
      <div class="text-center md:text-left mt-2">
        <div class="font-heading font-bold text-xl text-brand-dark">{OWNER['name']}</div>
        <div class="font-body text-brand-mid text-sm">{OWNER['role']}</div>
      </div>
    </div>
    <!-- Text -->
    <div>
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Sobre nosotros</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-6">Marketing digital<br/>hecho por alguien<br/>de acá.</h2>
      <p class="font-body text-brand-mid text-base leading-relaxed mb-8">
        {OWNER['bio']}
      </p>
      <div class="space-y-5">
        {values_html}
      </div>
    </div>
  </div>
</section>'''


def build_contact(brand):
    service_options = "\n".join(
        f'            <option value="{s["title"]}">{s["title"]}</option>'
        for s in SERVICES
    )
    return f'''
<section id="contacto" class="py-20 px-6 lg:px-16 bg-brand-light">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-14">
      <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Contacto</span>
      <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-brand-dark mt-3 mb-4">¿Hablamos?</h2>
      <p class="font-body text-brand-mid text-lg max-w-xl mx-auto">El primer diagnóstico es gratis. Contanos de tu negocio y te decimos exactamente qué haríamos para hacerlo crecer.</p>
    </div>
    <div class="grid md:grid-cols-2 gap-12 items-start">
      <!-- Form -->
      <form action="mailto:{brand['email']}" method="post" enctype="text/plain"
            class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 space-y-5">
        <div class="grid sm:grid-cols-2 gap-5">
          <div>
            <label class="block font-body font-medium text-brand-dark text-sm mb-1.5">Nombre *</label>
            <input type="text" name="nombre" required placeholder="Tu nombre"
                   class="w-full border border-gray-200 rounded-xl px-4 py-3 font-body text-sm text-brand-dark placeholder-gray-400 focus:outline-none focus:border-brand-blue transition-colors"/>
          </div>
          <div>
            <label class="block font-body font-medium text-brand-dark text-sm mb-1.5">Email *</label>
            <input type="email" name="email" required placeholder="tu@email.com"
                   class="w-full border border-gray-200 rounded-xl px-4 py-3 font-body text-sm text-brand-dark placeholder-gray-400 focus:outline-none focus:border-brand-blue transition-colors"/>
          </div>
        </div>
        <div>
          <label class="block font-body font-medium text-brand-dark text-sm mb-1.5">Teléfono (opcional)</label>
          <input type="tel" name="telefono" placeholder="02284 XXXXXX"
                 class="w-full border border-gray-200 rounded-xl px-4 py-3 font-body text-sm text-brand-dark placeholder-gray-400 focus:outline-none focus:border-brand-blue transition-colors"/>
        </div>
        <div>
          <label class="block font-body font-medium text-brand-dark text-sm mb-1.5">Servicio de interés</label>
          <select name="servicio"
                  class="w-full border border-gray-200 rounded-xl px-4 py-3 font-body text-sm text-brand-dark focus:outline-none focus:border-brand-blue transition-colors bg-white">
            <option value="">Seleccioná un servicio...</option>
{service_options}
            <option value="No sé / quiero un diagnóstico">No sé / quiero un diagnóstico gratuito</option>
          </select>
        </div>
        <div>
          <label class="block font-body font-medium text-brand-dark text-sm mb-1.5">Mensaje *</label>
          <textarea name="mensaje" required rows="4" placeholder="Contanos de tu negocio y qué querés lograr..."
                    class="w-full border border-gray-200 rounded-xl px-4 py-3 font-body text-sm text-brand-dark placeholder-gray-400 focus:outline-none focus:border-brand-blue transition-colors resize-none"></textarea>
        </div>
        <button type="submit"
                class="w-full bg-brand-blue hover:bg-brand-blue-dark text-white font-body font-semibold py-3.5 rounded-xl transition-colors text-base">
          Enviar mensaje
        </button>
      </form>

      <!-- Contact info -->
      <div class="space-y-6">
        <div class="bg-white rounded-2xl p-6 border border-gray-100">
          <h3 class="font-heading font-bold text-lg text-brand-dark mb-4">O contactanos directamente</h3>
          <div class="space-y-4">
            <a href="https://wa.me/{brand['whatsapp_number']}?text={brand['whatsapp_message']}" target="_blank" rel="noopener"
               class="flex items-center gap-4 p-4 rounded-xl bg-[#25D366]/8 border border-[#25D366]/20 hover:bg-[#25D366]/15 transition-colors group">
              <div class="w-10 h-10 rounded-full bg-[#25D366] flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.126.553 4.122 1.524 5.854L0 24l6.335-1.502A11.954 11.954 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.493-5.18-1.357l-.37-.219-3.835.909.971-3.75-.241-.385A9.937 9.937 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
              </div>
              <div>
                <div class="font-body font-semibold text-brand-dark text-sm">WhatsApp</div>
                <div class="font-body text-brand-mid text-sm">{brand['whatsapp_display']}</div>
              </div>
            </a>
            <a href="mailto:{brand['email']}"
               class="flex items-center gap-4 p-4 rounded-xl bg-brand-blue/5 border border-brand-blue/15 hover:bg-brand-blue/10 transition-colors">
              <div class="w-10 h-10 rounded-full bg-brand-blue/15 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-brand-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              </div>
              <div>
                <div class="font-body font-semibold text-brand-dark text-sm">Email</div>
                <div class="font-body text-brand-mid text-sm">{brand['email']}</div>
              </div>
            </a>
            <div class="flex items-center gap-4 p-4 rounded-xl bg-gray-50 border border-gray-100">
              <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-brand-mid" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              </div>
              <div>
                <div class="font-body font-semibold text-brand-dark text-sm">Ubicación</div>
                <div class="font-body text-brand-mid text-sm">Olavarría, Buenos Aires, Argentina</div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-brand-blue rounded-2xl p-6 text-white">
          <div class="font-heading font-bold text-lg mb-2">Diagnóstico digital gratuito</div>
          <p class="font-body text-blue-100 text-sm leading-relaxed mb-4">Analizamos tu presencia digital actual y la de tu competencia, sin costo. Te decimos exactamente qué haríamos para hacer crecer tu negocio.</p>
          <a href="https://wa.me/{brand['whatsapp_number']}?text=Hola%2C%20me%20interesa%20el%20diagn%C3%B3stico%20digital%20gratuito." target="_blank" rel="noopener"
             class="inline-flex items-center gap-2 bg-white text-brand-blue font-body font-semibold text-sm px-5 py-2.5 rounded-full hover:bg-blue-50 transition-colors">
            Quiero el diagnóstico
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>'''


def build_floating_whatsapp(brand):
    return f'''
<a href="https://wa.me/{brand['whatsapp_number']}?text={brand['whatsapp_message']}"
   target="_blank" rel="noopener"
   aria-label="Chateá con OLA Digital por WhatsApp"
   class="whatsapp-pulse fixed bottom-6 right-6 z-50 w-14 h-14 bg-[#25D366] hover:bg-[#1ebe5a] rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 group">
  <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
    <path d="M12 0C5.373 0 0 5.373 0 12c0 2.126.553 4.122 1.524 5.854L0 24l6.335-1.502A11.954 11.954 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.493-5.18-1.357l-.37-.219-3.835.909.971-3.75-.241-.385A9.937 9.937 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
  </svg>
  <span class="absolute right-16 bg-brand-dark text-white text-xs font-body font-medium px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
    ¡Chateá con nosotros!
  </span>
</a>'''


def build_footer(brand):
    return f'''
<footer class="bg-brand-dark text-white py-14 px-6 lg:px-16">
  <div class="max-w-6xl mx-auto">
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
      <!-- Brand -->
      <div class="sm:col-span-2 lg:col-span-1">
        <img src="assets/logo-white.svg" alt="OLA Digital" class="h-10 w-auto mb-3"/>
        <div class="w-8 h-0.5 bg-brand-blue mb-4 rounded"></div>
        <p class="font-body text-slate-400 text-sm leading-relaxed mb-5">{brand['tagline']}<br/>Olavarría, Buenos Aires, Argentina.</p>
        <div class="flex gap-3">
          <a href="#" aria-label="Instagram" class="w-9 h-9 rounded-full bg-white/10 hover:bg-brand-blue flex items-center justify-center transition-colors">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
          </a>
          <a href="#" aria-label="Facebook" class="w-9 h-9 rounded-full bg-white/10 hover:bg-brand-blue flex items-center justify-center transition-colors">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          </a>
          <a href="#" aria-label="LinkedIn" class="w-9 h-9 rounded-full bg-white/10 hover:bg-brand-blue flex items-center justify-center transition-colors">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
        </div>
      </div>
      <!-- Navigation -->
      <div>
        <div class="font-body font-semibold text-white text-sm mb-4">Navegación</div>
        <ul class="space-y-2">
          {''.join(f'<li><a href="{href}" class="font-body text-slate-400 hover:text-white text-sm transition-colors">{label}</a></li>' for href, label in [("#servicios", "Servicios"), ("#trabajos", "Trabajos"), ("#testimonios", "Testimonios"), ("#nosotros", "Nosotros"), ("#contacto", "Contacto")])}
        </ul>
      </div>
      <!-- Services -->
      <div>
        <div class="font-body font-semibold text-white text-sm mb-4">Servicios</div>
        <ul class="space-y-2">
          {''.join(f'<li><a href="#servicios" class="font-body text-slate-400 hover:text-white text-sm transition-colors">{s["title"]}</a></li>' for s in SERVICES)}
        </ul>
      </div>
      <!-- Contact -->
      <div>
        <div class="font-body font-semibold text-white text-sm mb-4">Contacto</div>
        <ul class="space-y-3">
          <li class="flex items-start gap-2">
            <svg class="w-4 h-4 text-brand-blue mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.126.553 4.122 1.524 5.854L0 24l6.335-1.502A11.954 11.954 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.885 0-3.65-.493-5.18-1.357l-.37-.219-3.835.909.971-3.75-.241-.385A9.937 9.937 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
            <a href="https://wa.me/{brand['whatsapp_number']}" class="font-body text-slate-400 hover:text-white text-sm transition-colors">{brand['whatsapp_display']}</a>
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-4 h-4 text-brand-blue mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            <a href="mailto:{brand['email']}" class="font-body text-slate-400 hover:text-white text-sm transition-colors">{brand['email']}</a>
          </li>
          <li class="flex items-start gap-2">
            <svg class="w-4 h-4 text-brand-blue mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            <span class="font-body text-slate-400 text-sm">Olavarría, Buenos Aires</span>
          </li>
        </ul>
      </div>
    </div>
    <div class="border-t border-white/10 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
      <p class="font-body text-slate-500 text-sm">© 2025 OLA Digital — Olavarría, Buenos Aires, Argentina.</p>
      <p class="font-body text-slate-600 text-xs">Hecho con ❤️ en Olavarría</p>
    </div>
  </div>
</footer>'''


def _stat_visual(p):
    accent = p["color_accent"]
    accent2 = p["color_accent2"]
    bg = p["color_bg"]
    lines = p["stat_label"].split("\n")
    label_html = "<br/>".join(lines)
    # Abstract radial pattern SVG in brand color
    pattern = (
        f'<svg class="absolute inset-0 w-full h-full" viewBox="0 0 340 200" fill="none" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="280" cy="100" r="120" fill="{accent}" opacity="0.07"/>'
        f'<circle cx="280" cy="100" r="80" fill="{accent}" opacity="0.07"/>'
        f'<circle cx="280" cy="100" r="45" fill="{accent}" opacity="0.08"/>'
        f'<circle cx="60" cy="180" r="60" fill="{accent2}" opacity="0.05"/>'
        f'<line x1="30" y1="30" x2="310" y2="170" stroke="{accent}" stroke-width="1" opacity="0.06"/>'
        f'<line x1="30" y1="170" x2="310" y2="30" stroke="{accent}" stroke-width="1" opacity="0.04"/>'
        f'</svg>'
    )
    return (
        f'<div class="rounded-2xl overflow-hidden relative" style="background:{bg};height:190px">'
        f'{pattern}'
        f'<div class="relative z-10 h-full flex flex-col justify-between p-5">'
        f'<div class="text-3xl">{p["icon"]}</div>'
        f'<div>'
        f'<div class="font-heading font-extrabold leading-none mb-1" style="font-size:3.5rem;color:{accent}">{p["stat_number"]}</div>'
        f'<div class="font-body font-semibold text-sm leading-snug" style="color:rgba(255,255,255,0.7)">{label_html}</div>'
        f'</div>'
        f'<div class="font-body text-xs font-medium px-2.5 py-1 rounded-full self-start" style="background:{accent}25;color:{accent}">{p["stat_sub"]}</div>'
        f'</div>'
        f'</div>'
    )


def _website_mockup(p):
    accent = p["color_accent"]
    bg = p["color_bg"]
    return (
        f'<div class="rounded-2xl overflow-hidden border border-white/10" style="background:#0a0a0a">'
        f'<div class="flex items-center gap-1.5 px-3 py-2 border-b border-white/10" style="background:#1a1a1a">'
        f'<span class="w-2.5 h-2.5 rounded-full" style="background:#ff5f57"></span>'
        f'<span class="w-2.5 h-2.5 rounded-full" style="background:#febc2e"></span>'
        f'<span class="w-2.5 h-2.5 rounded-full" style="background:#28c840"></span>'
        f'<div class="flex-1 mx-2 px-3 py-1 rounded-full text-center font-body" style="background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.4);font-size:11px">{p["link_label"]}</div>'
        f'</div>'
        f'<div class="relative overflow-hidden" style="height:140px">'
        f'<img src="{p["photo_url"]}" alt="{p["client"]}" class="w-full h-full object-cover" loading="lazy"'
        f'     onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'"/>'
        f'<div class="absolute inset-0 items-center justify-center text-5xl hidden" style="background:{bg}">🗺️</div>'
        f'<div class="absolute bottom-0 left-0 right-0 px-3 py-2" style="background:linear-gradient(to top,{bg}f0,transparent)">'
        f'<img src="{p["logo_url"]}" alt="Maroni Maps logo" class="h-5 object-contain" loading="lazy" onerror="this.style.display=\'none\'"/>'
        f'</div></div>'
        f'<div class="px-3 py-2.5 flex items-center gap-3 border-t border-white/8" style="background:#111">'
        f'<div class="h-2 rounded-full w-14" style="background:{accent}50"></div>'
        f'<div class="h-2 rounded-full flex-1 bg-white/10"></div>'
        f'<div class="h-6 w-16 rounded-full text-center font-body font-semibold flex items-center justify-center" style="background:{accent};color:#0f172a;font-size:11px">Comprar</div>'
        f'</div>'
        f'</div>'
    )


def build_portfolio(brand):
    cards_html = ""
    for p in PORTFOLIO:
        tags_html = "".join(
            f'<span class="font-body text-xs font-medium px-2.5 py-1 rounded-full" style="background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.85)">{t}</span>'
            for t in p["tags"]
        )
        if p["display"] == "stat":
            visual = _stat_visual(p)
        else:
            visual = _website_mockup(p)

        cards_html += f'''
        <div class="portfolio-card rounded-2xl overflow-hidden shadow-xl flex flex-col" style="background:{p['color_bg']}">
          <!-- Header -->
          <div class="p-5 pb-3">
            <div class="flex items-start justify-between mb-3">
              <div>
                <div class="font-body text-xs font-semibold uppercase tracking-widest mb-0.5" style="color:{p['color_accent']}">{p["category"]}</div>
                <h3 class="font-heading font-extrabold text-xl text-white">{p["client"]}</h3>
              </div>
              <a href="{p["link"]}" target="_blank" rel="noopener"
                 class="flex items-center gap-1 text-xs font-body opacity-50 hover:opacity-90 transition-opacity mt-1" style="color:rgba(255,255,255,0.8)">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                {p["link_label"]}
              </a>
            </div>
            <div class="flex flex-wrap gap-1.5">
              {tags_html}
            </div>
          </div>
          <!-- Visual mockup -->
          <div class="mx-4">
            {visual}
          </div>
          <!-- Result + description -->
          <div class="p-5 pt-4 flex flex-col gap-3">
            <p class="font-body text-sm leading-relaxed" style="color:rgba(255,255,255,0.6)">{p["description"]}</p>
            <div class="flex items-center gap-2 rounded-xl px-3 py-2.5" style="background:{p['color_accent']}22;border:1px solid {p['color_accent']}44">
              <svg class="w-4 h-4 flex-shrink-0" style="color:{p['color_accent']}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
              <span class="font-body font-semibold text-sm" style="color:{p['color_accent']}">{p["result"]}</span>
            </div>
          </div>
        </div>'''

    return f'''
<section id="trabajos" class="py-20 px-6 lg:px-16 bg-brand-dark overflow-hidden">
  <div class="max-w-6xl mx-auto">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12">
      <div>
        <span class="font-body font-semibold text-brand-blue text-sm uppercase tracking-widest">Trabajos realizados</span>
        <h2 class="font-heading font-extrabold text-3xl lg:text-4xl text-white mt-3 mb-3">Lo que hicimos<br/>por nuestros clientes</h2>
        <p class="font-body text-slate-400 text-base max-w-xl">Resultados reales para negocios de Olavarría y Argentina. Deslizá para ver cada caso.</p>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <button id="portfolio-prev" onclick="portfolioScroll(-1)"
                class="w-10 h-10 rounded-full border border-white/20 hover:border-brand-blue hover:bg-brand-blue/10 flex items-center justify-center transition-all text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <button id="portfolio-next" onclick="portfolioScroll(1)"
                class="w-10 h-10 rounded-full border border-white/20 hover:border-brand-blue hover:bg-brand-blue/10 flex items-center justify-center transition-all text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
      </div>
    </div>

    <!-- Slider -->
    <div id="portfolio-track" class="portfolio-track">
      {cards_html}
    </div>

    <!-- Dots -->
    <div class="flex justify-center gap-2 mt-6" id="portfolio-dots">
      {''.join(f'<button onclick="portfolioGoTo({i})" class="portfolio-dot w-2 h-2 rounded-full transition-all" style="background:rgba(255,255,255,{0.6 if i==0 else 0.25})"></button>' for i in range(len(PORTFOLIO)))}
    </div>

    <div class="mt-14 text-center">
      <a href="#contacto"
         class="inline-flex items-center gap-2 bg-brand-blue hover:bg-brand-blue-dark text-white font-body font-semibold px-8 py-4 rounded-full transition-colors text-base">
        Quiero resultados así para mi negocio
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
      </a>
    </div>
  </div>
</section>

<script>
  const track = document.getElementById('portfolio-track');
  const dots = document.querySelectorAll('.portfolio-dot');
  let current = 0;

  function updateDots(idx) {{
    dots.forEach((d, i) => {{
      d.style.background = i === idx ? '#0EA5E9' : 'rgba(255,255,255,0.25)';
      d.style.width = i === idx ? '24px' : '8px';
    }});
  }}

  function portfolioGoTo(idx) {{
    const cards = track.querySelectorAll('.portfolio-card');
    if (!cards[idx]) return;
    current = idx;
    track.scrollTo({{ left: cards[idx].offsetLeft - 24, behavior: 'smooth' }});
    updateDots(idx);
  }}

  function portfolioScroll(dir) {{
    const cards = track.querySelectorAll('.portfolio-card');
    current = Math.max(0, Math.min(cards.length - 1, current + dir));
    portfolioGoTo(current);
  }}

  track.addEventListener('scroll', () => {{
    const cards = track.querySelectorAll('.portfolio-card');
    let closest = 0, minDist = Infinity;
    cards.forEach((c, i) => {{
      const dist = Math.abs(c.offsetLeft - track.scrollLeft - 24);
      if (dist < minDist) {{ minDist = dist; closest = i; }}
    }});
    if (closest !== current) {{ current = closest; updateDots(closest); }}
  }});
</script>'''


def assemble_html(brand):
    return "\n".join([
        build_head(brand),
        "<body class='font-body bg-white text-brand-dark antialiased'>",
        build_nav(brand),
        build_hero(brand),
        build_services(brand),
        build_local(brand),
        build_process(brand),
        build_portfolio(brand),
        build_testimonials(brand),
        build_about(brand),
        build_contact(brand),
        build_floating_whatsapp(brand),
        build_footer(brand),
        "</body>",
        "</html>",
    ])


def run():
    root = Path(__file__).parent.parent
    website_dir = root / "website"
    assets_dir = website_dir / "assets"
    css_dir = assets_dir / "css"

    for d in [website_dir, assets_dir, css_dir]:
        d.mkdir(parents=True, exist_ok=True)

    files = {
        website_dir / "index.html":           assemble_html(BRAND),
        assets_dir / "logo.svg":              build_logo_svg(BRAND),
        assets_dir / "logo-white.svg":        build_logo_white_svg(BRAND),
        assets_dir / "logo-icon.svg":         build_logo_icon_svg(BRAND),
        assets_dir / "favicon.svg":           build_favicon_svg(BRAND),
        css_dir / "custom.css":               build_custom_css(BRAND),
    }

    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
        size_kb = len(content.encode()) / 1024
        print(f"  ✓ {path.relative_to(root)}  ({size_kb:.1f} KB)")

    print(f"\nSitio generado en: {website_dir}")
    print(f"Abrí {website_dir / 'index.html'} en tu navegador para previsualizarlo.")


if __name__ == "__main__":
    run()
