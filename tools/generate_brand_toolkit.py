"""
Generates a complete OLA Digital brand toolkit as a standalone HTML file.
Outputs: brand-toolkit/index.html
Usage: python3 tools/generate_brand_toolkit.py
Run generate_logo_ai.py first to populate AI-generated images.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
TOOLKIT_DIR = ROOT / "brand-toolkit"
ASSETS_DIR = TOOLKIT_DIR / "assets"

BRAND = {
    "name": "OLA Digital",
    "tagline": "Hacemos crecer negocios en Olavarría.",
    "email": "hola@oladigital.com.ar",
    "whatsapp": "+54 9 11 6231-0105",
    "city": "Olavarría, Buenos Aires",
    "version": "1.0",
    "year": "2025",
}

COLORS = [
    {"name": "Ocean Blue",    "hex": "#0369A1", "role": "Primary Dark",   "use": "Headlines, deep backgrounds"},
    {"name": "Sky Blue",      "hex": "#0EA5E9", "role": "Primary",        "use": "Buttons, links, accents"},
    {"name": "Cyan Wave",     "hex": "#06B6D4", "role": "Primary Light",  "use": "Highlights, gradients"},
    {"name": "Sky Light",     "hex": "#38BDF8", "role": "Tint",           "use": "Hover states, light backgrounds"},
    {"name": "Mandarina",     "hex": "#F97316", "role": "Accent",         "use": "CTAs, urgency, warmth"},
    {"name": "Amber",         "hex": "#F59E0B", "role": "Accent Alt",     "use": "Badges, stars, highlights"},
    {"name": "Dark Navy",     "hex": "#0F172A", "role": "Dark",           "use": "Body text, dark backgrounds"},
    {"name": "Slate",         "hex": "#334155", "role": "Mid",            "use": "Secondary text, dividers"},
    {"name": "Cool Grey",     "hex": "#94A3B8", "role": "Subtle",         "use": "Placeholders, disabled states"},
    {"name": "Ice",           "hex": "#F0F9FF", "role": "Background",     "use": "Section backgrounds, cards"},
    {"name": "White",         "hex": "#FFFFFF", "role": "Base",           "use": "Primary background, text on dark"},
]

TYPOGRAPHY = [
    {"family": "Plus Jakarta Sans", "role": "Display & Headlines", "weights": "700 · 800", "usage": "Hero text, section titles, logo wordmark", "sample": "Hacemos crecer\nnegocios en internet."},
    {"family": "Inter",             "role": "Body & UI",           "weights": "400 · 500 · 600", "usage": "Body copy, navigation, forms, captions", "sample": "Agencia de marketing digital\nen Olavarría, Buenos Aires."},
]

LOGO_RULES = [
    ("✓ DO", "#16a34a", [
        "Use on white or very light backgrounds",
        "Use logo-white.svg on dark or coloured backgrounds",
        "Maintain clear space equal to the height of the 'O' on all sides",
        "Scale proportionally — never stretch or squish",
        "Use logo-icon.svg when space is limited (app icons, favicons, profile pics)",
    ]),
    ("✗ DON'T", "#dc2626", [
        "Don't change the logo colours",
        "Don't add drop shadows, outlines or glows to the mark",
        "Don't place the colour logo on busy photos without a white backing",
        "Don't rotate or skew the logo",
        "Don't use the logotype without the wave mark beside it",
    ]),
]

VOICE = [
    ("Cercano", "Hablamos como vecinos, no como corporaciones. Tuteamos siempre."),
    ("Directo", "Sin tecnicismos innecesarios. Si podés decirlo en menos palabras, hacelo."),
    ("Confiado", "Sabemos lo que hacemos. No pedimos disculpas por nuestra opinión."),
    ("Local",   "Mencionamos Olavarría por nombre. Conocemos el barrio. Eso es ventaja."),
]


def _color_card(c):
    r, g, b = int(c["hex"][1:3], 16), int(c["hex"][3:5], 16), int(c["hex"][5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    txt = "#ffffff" if brightness < 128 else "#0F172A"
    return (
        f'<div class="color-card" style="--bg:{c["hex"]};--txt:{txt}">'
        f'<div class="swatch" style="background:{c["hex"]}"></div>'
        f'<div class="color-info">'
        f'<span class="color-name">{c["name"]}</span>'
        f'<code class="color-hex">{c["hex"]}</code>'
        f'<span class="color-role">{c["role"]}</span>'
        f'<span class="color-use">{c["use"]}</span>'
        f'</div></div>'
    )


def _type_specimen(t):
    lines = t["sample"].split("\n")
    sample_html = "<br/>".join(lines)
    size = "2.4rem" if t["role"].startswith("Display") else "1.5rem"
    weight = "800" if t["role"].startswith("Display") else "400"
    return (
        f'<div class="type-card">'
        f'<div class="type-meta">'
        f'<span class="type-family">{t["family"]}</span>'
        f'<span class="type-role badge">{t["role"]}</span>'
        f'</div>'
        f'<div class="type-weights">Weights used: <strong>{t["weights"]}</strong></div>'
        f'<div class="type-usage">{t["usage"]}</div>'
        f'<div class="type-sample" style="font-family:\'{t["family"]}\', sans-serif;font-size:{size};font-weight:{weight}">{sample_html}</div>'
        f'</div>'
    )


def _logo_rule_section(label, color, items):
    li = "".join(f'<li>{item}</li>' for item in items)
    return (
        f'<div class="rule-block">'
        f'<h4 style="color:{color}">{label}</h4>'
        f'<ul>{li}</ul>'
        f'</div>'
    )


def _logo_preview(src, bg, label, border=False):
    border_style = "border:1px solid #e2e8f0;" if border else ""
    return (
        f'<div class="logo-preview" style="background:{bg};{border_style}">'
        f'<img src="assets/logo{"" if bg == "#ffffff" or bg == "#F0F9FF" else "-white"}.svg" '
        f'     alt="OLA Digital logo on {label}" />'
        f'<span class="preview-label">{label}</span>'
        f'</div>'
    )


def _ai_image_section():
    images = [
        # C-series (B6/B7 style evolution)
        ("logo-c1.svg", "Dark + horizon line — OLA sunset",    "#050A14", False),
        ("logo-c2.svg", "Dark hexagon grid — OLA electric white","#080C18", False),
        ("logo-c3.svg", "Dark stacked — OLA cyan-to-blue grid","#060D1F", False),
        ("logo-c4.svg", "Dark circle emblem + wordmark",       "#080C18", False),
        ("logo-c5.svg", "Hexagon mark + OLA horizontal",       "#ffffff", True),
        ("logo-c6.svg", "Bold O lettermark + wave inside",     "#ffffff", True),
        ("logo-c7.svg", "Shield/crest — OLA inside shield",    "#f8fafc", True),
        ("logo-c8.svg", "Diamond refined — gradient fill",     "#ffffff", True),
        # B-series
        ("logo-b1.svg", "Neon glow — dark electric",          "#0A0F1E", False),
        ("logo-b2.svg", "Circle O wave mark",                  "#ffffff", True),
        ("logo-b3.svg", "Bold stacked + orange accent",        "#ffffff", True),
        ("logo-b4.svg", "Pill badge — gradient capsule",       "#f8fafc", True),
        ("logo-b5.svg", "Signal arcs + orange dot",            "#ffffff", True),
        ("logo-b6.svg", "Retro synthwave grid",                "#0A0118", False),
        ("logo-b7.svg", "OD monogram diamond",                 "#ffffff", True),
        ("logo-b8.svg", "Split color O·L·A + digital",         "#ffffff", True),
        ("logo-ai-full.png", "Concepto AI (Pollinations)",     "#f8fafc", True),
    ]
    cards = ""
    for fname, label, bg, border in images:
        fpath = ASSETS_DIR / fname
        exists = fpath.exists()
        if exists:
            border_style = "border:1px solid #e2e8f0;" if border else ""
            cards += (
                f'<div class="ai-card">'
                f'<div class="ai-img-wrap" style="background:{bg};{border_style}">'
                f'<img src="assets/{fname}" alt="{label}" loading="lazy"/>'
                f'</div>'
                f'<p class="ai-label">{label}</p>'
                f'</div>'
            )
        else:
            cards += (
                f'<div class="ai-card ai-missing">'
                f'<div class="ai-img-wrap" style="background:#1e293b">'
                f'<span>Ejecutá<br/><code>generate_logo_ai.py</code><br/>para generar</span>'
                f'</div>'
                f'<p class="ai-label">{label}</p>'
                f'</div>'
            )
    return cards


def build_toolkit_html():
    color_cards = "".join(_color_card(c) for c in COLORS)
    type_cards = "".join(_type_specimen(t) for t in TYPOGRAPHY)
    rule_sections = "".join(_logo_rule_section(l, c, i) for l, c, i in LOGO_RULES)
    voice_cards = "".join(
        f'<div class="voice-card"><h4>{v[0]}</h4><p>{v[1]}</p></div>'
        for v in VOICE
    )
    ai_cards = _ai_image_section()

    logo_previews = (
        _logo_preview("assets/logo.svg", "#ffffff", "Fondo blanco", border=True) +
        _logo_preview("assets/logo.svg", "#F0F9FF", "Fondo claro", border=True) +
        _logo_preview("assets/logo-white.svg", "#0F172A", "Fondo oscuro") +
        _logo_preview("assets/logo-white.svg", "#0EA5E9", "Fondo primario") +
        _logo_preview("assets/logo-white.svg", "#F97316", "Fondo acento")
    )

    # SVG logo files available
    logo_files = [
        ("logo.svg",       "Logo completo",    "Uso principal — fondos blancos y claros"),
        ("logo-white.svg", "Logo blanco",       "Fondos oscuros, fotos, colores sólidos"),
        ("logo-icon.svg",  "Ícono / badge",     "App icon, WhatsApp, redes sociales, favicon"),
        ("favicon.svg",    "Favicon",           "Pestaña del navegador"),
    ]
    file_rows = "".join(
        f'<tr><td><code>{f}</code></td><td>{n}</td><td class="muted">{u}</td>'
        f'<td><a href="assets/{f}" download class="dl-btn">↓ Descargar</a></td></tr>'
        for f, n, u in logo_files
    )

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>OLA Digital — Brand Toolkit v{BRAND["version"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:       #0A0F1E;
      --surface:  #111827;
      --surface2: #1E293B;
      --border:   rgba(255,255,255,0.08);
      --text:     #E2E8F0;
      --muted:    #64748B;
      --blue:     #0EA5E9;
      --cyan:     #06B6D4;
      --orange:   #F97316;
      --green:    #22C55E;
      --red:      #EF4444;
      --font-head: 'Plus Jakarta Sans', sans-serif;
      --font-body: 'Inter', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --radius:   16px;
      --radius-sm: 8px;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      font-size: 15px;
    }}

    /* Layout */
    .sidebar {{
      position: fixed; top: 0; left: 0; bottom: 0; width: 220px;
      background: var(--surface); border-right: 1px solid var(--border);
      padding: 28px 20px; overflow-y: auto; z-index: 100;
    }}
    .sidebar-logo {{ margin-bottom: 32px; }}
    .sidebar-logo img {{ height: 36px; width: auto; }}
    .sidebar-section {{ font-size: 10px; font-weight: 600; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; margin: 20px 0 8px; }}
    .sidebar nav a {{
      display: block; padding: 7px 12px; border-radius: var(--radius-sm);
      color: var(--muted); text-decoration: none; font-size: 13px; font-weight: 500;
      transition: all 0.15s;
    }}
    .sidebar nav a:hover {{ background: rgba(255,255,255,0.06); color: var(--text); }}
    .sidebar-version {{ font-size: 11px; color: var(--muted); margin-top: auto; padding-top: 20px; border-top: 1px solid var(--border); }}

    .main {{ margin-left: 220px; padding: 48px 56px; max-width: 1100px; }}

    /* Sections */
    .section {{ margin-bottom: 80px; }}
    .section-tag {{ font-size: 11px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--blue); margin-bottom: 8px; }}
    h2.section-title {{ font-family: var(--font-head); font-size: 2rem; font-weight: 800; color: white; margin-bottom: 6px; }}
    .section-desc {{ color: var(--muted); max-width: 560px; margin-bottom: 36px; font-size: 14px; }}
    h3 {{ font-family: var(--font-head); font-weight: 700; font-size: 1rem; color: white; margin-bottom: 16px; }}

    /* Cover */
    .cover {{
      background: linear-gradient(135deg, #0C1A2E 0%, #0F2A47 50%, #0C1A2E 100%);
      border-radius: var(--radius); padding: 72px 56px; margin-bottom: 80px;
      border: 1px solid var(--border); position: relative; overflow: hidden;
    }}
    .cover::before {{
      content: ''; position: absolute; right: -80px; top: -80px;
      width: 400px; height: 400px; border-radius: 50%;
      background: radial-gradient(circle, rgba(14,165,233,0.12) 0%, transparent 70%);
    }}
    .cover-logo {{ margin-bottom: 32px; }}
    .cover-logo img {{ height: 56px; width: auto; }}
    .cover h1 {{ font-family: var(--font-head); font-size: 3rem; font-weight: 800; color: white; margin-bottom: 12px; line-height: 1.1; }}
    .cover-sub {{ font-size: 1.1rem; color: rgba(255,255,255,0.55); max-width: 480px; margin-bottom: 36px; }}
    .cover-meta {{ display: flex; gap: 32px; }}
    .cover-meta div {{ font-size: 12px; color: var(--muted); }}
    .cover-meta strong {{ display: block; color: var(--text); font-size: 14px; font-weight: 600; }}

    /* Colors */
    .color-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }}
    .color-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
    .swatch {{ height: 80px; }}
    .color-info {{ padding: 12px 14px; display: flex; flex-direction: column; gap: 3px; }}
    .color-name {{ font-weight: 600; font-size: 13px; color: white; }}
    .color-hex {{ font-family: var(--font-mono); font-size: 12px; color: var(--blue); }}
    .color-role {{ font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
    .color-use {{ font-size: 11px; color: var(--muted); }}

    /* Gradient bar */
    .gradient-bar {{
      height: 48px; border-radius: var(--radius-sm); margin-bottom: 12px;
      background: linear-gradient(90deg, #0C4A6E, #0369A1, #0EA5E9, #06B6D4, #38BDF8);
    }}
    .gradient-label {{ font-size: 12px; color: var(--muted); margin-bottom: 32px; }}

    /* Typography */
    .type-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 28px 28px 32px; margin-bottom: 20px;
    }}
    .type-meta {{ display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }}
    .type-family {{ font-family: var(--font-head); font-weight: 700; font-size: 1rem; color: white; }}
    .badge {{
      font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
      background: rgba(14,165,233,0.15); color: var(--blue); padding: 3px 8px; border-radius: 4px;
    }}
    .type-weights {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
    .type-usage {{ font-size: 12px; color: var(--muted); margin-bottom: 20px; }}
    .type-sample {{ color: white; line-height: 1.2; }}

    /* Logo usage */
    .logo-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 36px; }}
    .logo-preview {{
      border-radius: var(--radius); padding: 32px 24px;
      display: flex; flex-direction: column; align-items: center; gap: 16px;
    }}
    .logo-preview img {{ height: 44px; width: auto; max-width: 100%; }}
    .preview-label {{ font-size: 11px; color: var(--muted); text-align: center; }}

    /* Rules */
    .rules-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 36px; }}
    .rule-block {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; }}
    .rule-block h4 {{ font-weight: 700; font-size: 13px; margin-bottom: 14px; }}
    .rule-block ul {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
    .rule-block li {{ font-size: 13px; color: var(--muted); padding-left: 16px; position: relative; }}
    .rule-block li::before {{ content: '—'; position: absolute; left: 0; color: var(--border); }}

    /* File table */
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--muted); text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); }}
    td {{ padding: 12px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }}
    td code {{ font-family: var(--font-mono); font-size: 12px; color: var(--blue); }}
    .muted {{ color: var(--muted); }}
    .dl-btn {{
      font-size: 12px; font-weight: 600; color: var(--blue);
      text-decoration: none; padding: 4px 10px; border: 1px solid rgba(14,165,233,0.3);
      border-radius: 6px;
    }}
    .dl-btn:hover {{ background: rgba(14,165,233,0.1); }}

    /* AI images */
    .ai-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    .ai-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }}
    .ai-img-wrap {{
      padding: 20px; min-height: 180px;
      display: flex; align-items: center; justify-content: center;
    }}
    .ai-img-wrap img {{ width: 100%; height: auto; border-radius: var(--radius-sm); }}
    .ai-img-wrap span {{ color: var(--muted); font-size: 12px; text-align: center; line-height: 1.8; }}
    .ai-img-wrap code {{ color: var(--blue); }}
    .ai-label {{ font-size: 12px; color: var(--muted); padding: 12px 16px; border-top: 1px solid var(--border); }}

    /* Voice */
    .voice-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }}
    .voice-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 22px;
    }}
    .voice-card h4 {{ font-family: var(--font-head); font-weight: 700; font-size: 1.1rem; color: white; margin-bottom: 10px; }}
    .voice-card p {{ font-size: 13px; color: var(--muted); line-height: 1.6; }}

    /* Spacing scale */
    .spacing-row {{ display: flex; align-items: center; gap: 16px; margin-bottom: 10px; }}
    .spacing-box {{ background: rgba(14,165,233,0.15); border: 1px solid rgba(14,165,233,0.3); flex-shrink: 0; }}
    .spacing-label {{ font-family: var(--font-mono); font-size: 12px; color: var(--blue); width: 60px; }}
    .spacing-desc {{ font-size: 12px; color: var(--muted); }}

    @media (max-width: 900px) {{
      .sidebar {{ display: none; }}
      .main {{ margin-left: 0; padding: 24px 20px; }}
      .rules-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <img src="assets/logo-white.svg" alt="OLA Digital"/>
  </div>
  <div class="sidebar-section">Brand Toolkit</div>
  <nav>
    <a href="#cover">Portada</a>
    <a href="#logo">Logo</a>
    <a href="#ai">Conceptos AI</a>
    <a href="#colors">Colores</a>
    <a href="#typography">Tipografía</a>
    <a href="#voice">Voz de marca</a>
    <a href="#spacing">Espaciado</a>
    <a href="#files">Archivos</a>
  </nav>
  <div class="sidebar-version">
    <strong>{BRAND["name"]}</strong><br/>
    Brand Toolkit v{BRAND["version"]}<br/>
    {BRAND["year"]} · {BRAND["city"]}
  </div>
</aside>

<!-- Main content -->
<main class="main">

  <!-- Cover -->
  <div class="cover" id="cover">
    <div class="cover-logo">
      <img src="assets/logo-white.svg" alt="OLA Digital"/>
    </div>
    <h1>Brand<br/>Toolkit</h1>
    <p class="cover-sub">Todo lo que necesitás para usar la marca OLA Digital de forma consistente y profesional.</p>
    <div class="cover-meta">
      <div><strong>Versión</strong>{BRAND["version"]}</div>
      <div><strong>Año</strong>{BRAND["year"]}</div>
      <div><strong>Contacto</strong>{BRAND["email"]}</div>
    </div>
  </div>

  <!-- Logo section -->
  <section class="section" id="logo">
    <div class="section-tag">Identidad visual</div>
    <h2 class="section-title">El logo</h2>
    <p class="section-desc">El logo de OLA Digital está compuesto por el wave mark (badge con tres ondas) y el wordmark (OLA + DIGITAL). No se deben usar por separado salvo el ícono en contextos muy reducidos.</p>

    <h3>Variantes en diferentes fondos</h3>
    <div class="logo-grid">
      {logo_previews}
    </div>

    <h3>Reglas de uso</h3>
    <div class="rules-grid">
      {rule_sections}
    </div>
  </section>

  <!-- AI concepts -->
  <section class="section" id="ai">
    <div class="section-tag">Exploración creativa</div>
    <h2 class="section-title">Variantes de logo</h2>
    <p class="section-desc">Cuatro variantes SVG generadas por Claude + un concepto de imagen AI. Todos vectoriales y editables.</p>
    <div class="ai-grid">
      {ai_cards}
    </div>
  </section>

  <!-- Colors -->
  <section class="section" id="colors">
    <div class="section-tag">Paleta de color</div>
    <h2 class="section-title">Colores</h2>
    <p class="section-desc">La paleta de OLA Digital está inspirada en el océano — del azul profundo al cian brillante. El naranja mandarina aporta energía y urgencia.</p>

    <h3>Gradiente de marca</h3>
    <div class="gradient-bar"></div>
    <p class="gradient-label">linear-gradient(90deg, #0C4A6E → #0369A1 → #0EA5E9 → #06B6D4 → #38BDF8)</p>

    <div class="color-grid">
      {color_cards}
    </div>
  </section>

  <!-- Typography -->
  <section class="section" id="typography">
    <div class="section-tag">Sistema tipográfico</div>
    <h2 class="section-title">Tipografía</h2>
    <p class="section-desc">Dos familias: Plus Jakarta Sans para impacto visual, Inter para legibilidad en UI y cuerpo de texto.</p>
    {type_cards}

    <h3>Escala tipográfica</h3>
    <table style="margin-top:0">
      <thead><tr><th>Token</th><th>Size</th><th>Weight</th><th>Uso</th></tr></thead>
      <tbody>
        {''.join(f'<tr><td><code>{t}</code></td><td><code>{s}</code></td><td>{w}</td><td class="muted">{u}</td></tr>' for t,s,w,u in [
          ("display","3.75rem / 60px","800","Hero headline"),
          ("h1","2.25rem / 36px","800","Page title"),
          ("h2","1.875rem / 30px","700","Section title"),
          ("h3","1.25rem / 20px","700","Card title"),
          ("body-lg","1.125rem / 18px","400","Lead paragraph"),
          ("body","1rem / 16px","400","Body copy"),
          ("small","0.875rem / 14px","500","Secondary info"),
          ("caption","0.75rem / 12px","600","Labels, badges"),
        ])}
      </tbody>
    </table>
  </section>

  <!-- Voice -->
  <section class="section" id="voice">
    <div class="section-tag">Comunicación</div>
    <h2 class="section-title">Voz de marca</h2>
    <p class="section-desc">Cómo habla OLA Digital. Cuatro atributos que definen el tono en redes, web y comunicaciones.</p>
    <div class="voice-grid">
      {voice_cards}
    </div>
  </section>

  <!-- Spacing -->
  <section class="section" id="spacing">
    <div class="section-tag">Layout</div>
    <h2 class="section-title">Sistema de espaciado</h2>
    <p class="section-desc">Basado en múltiplos de 4px. Usar siempre valores de esta escala para mantener consistencia visual.</p>
    {''.join(
      f'<div class="spacing-row"><div class="spacing-label">{t}</div>'
      f'<div class="spacing-box" style="width:{px};height:{px}"></div>'
      f'<div class="spacing-desc">{desc}</div></div>'
      for t,px,desc in [
        ("4px","4px","Micro — separación de iconos"),
        ("8px","8px","XS — padding de badges, gap mínimo"),
        ("12px","12px","S — padding botones pequeños"),
        ("16px","16px","M — gap de grillas, padding de cards"),
        ("24px","24px","L — separación entre secciones menores"),
        ("32px","32px","XL — padding interno de secciones"),
        ("48px","48px","2XL — separación entre secciones"),
        ("64px","64px","3XL — padding de hero, footers"),
      ]
    )}
  </section>

  <!-- Files -->
  <section class="section" id="files">
    <div class="section-tag">Assets</div>
    <h2 class="section-title">Archivos del logo</h2>
    <p class="section-desc">Todos los archivos SVG son vectoriales — escalables a cualquier tamaño sin pérdida de calidad.</p>
    <table>
      <thead><tr><th>Archivo</th><th>Nombre</th><th>Uso</th><th></th></tr></thead>
      <tbody>{file_rows}</tbody>
    </table>
  </section>

</main>
</body>
</html>'''


def run():
    TOOLKIT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Copy SVG logos from website/assets to brand-toolkit/assets
    web_assets = ROOT / "website" / "assets"
    import shutil, glob
    base_logos = ["logo.svg", "logo-white.svg", "logo-icon.svg", "favicon.svg"]
    variant_logos = [p.name for p in web_assets.glob("logo-[bc]*.svg")]
    for svg in base_logos + sorted(variant_logos):
        src = web_assets / svg
        if src.exists():
            shutil.copy2(src, ASSETS_DIR / svg)
            print(f"  ✓ Copied {svg}")
    # Copy any AI-generated images
    for img in web_assets.glob("logo-ai-*.png"):
        shutil.copy2(img, ASSETS_DIR / img.name)
        print(f"  ✓ Copied {img.name}")

    html = build_toolkit_html()
    out = TOOLKIT_DIR / "index.html"
    out.write_text(html, encoding="utf-8")
    size_kb = len(html.encode()) / 1024
    print(f"  ✓ brand-toolkit/index.html  ({size_kb:.1f} KB)")
    print(f"\nBrand toolkit en: {TOOLKIT_DIR}")
    print(f"Abrí {out} en tu navegador.")


if __name__ == "__main__":
    run()
