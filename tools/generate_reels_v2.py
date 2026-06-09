#!/usr/bin/env python3
"""
Ola Digital — Reel Generator v2
Bigger, bolder, more animations. Reels 6–10.
1080×1920 · 30fps · no camera footage required.
"""

import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, concatenate_videoclips

W, H   = 1080, 1920
FPS    = 30
OUT    = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'reels')

# ── Palette ──────────────────────────────────────────────────────────────────
C_BLACK  = (0,   0,   0)
C_DARK   = (13,  27,  42)
C_TEAL   = (46,  196, 182)
C_RED    = (230, 57,  70)
C_YELLOW = (255, 209, 102)
C_WHITE  = (255, 255, 255)
C_GREY   = (140, 150, 165)
C_DKGREY = (50,  60,  75)

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_PATH = '/System/Library/Fonts/HelveticaNeue.ttc'
IDX_BLACK  = 9   # Condensed Black  ← headlines
IDX_BOLD   = 1   # Bold             ← subheads
IDX_REG    = 0   # Regular          ← small labels

_font_cache = {}

def F(size, weight='black'):
    idx = {'black': IDX_BLACK, 'bold': IDX_BOLD, 'reg': IDX_REG}[weight]
    key = (size, idx)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_PATH, size, index=idx)
    return _font_cache[key]


# ── Easing ───────────────────────────────────────────────────────────────────
def smooth(t, dur):
    p = min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0
    return p * p * (3 - 2 * p)

def expo_out(t, dur):
    p = min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0
    return 1 - (1 - p) ** 4

def spring(t, dur, overshoot=22):
    """Slides up from +overshoot px offset, overshoots slightly, settles."""
    if dur <= 0 or t >= dur:
        return 0
    p = t / dur
    decay   = (1 - p) ** 2
    oscil   = math.sin(p * math.pi * 2.2)
    offset  = int(overshoot * (1 - p) ** 2.5 - decay * oscil * 8)
    return offset

def zoom_scale(t, dur, from_=1.28, to=1.0):
    """Scale factor for zoom-in burst animation."""
    p = expo_out(t, dur)
    return from_ + (to - from_) * p


# ── Logo ──────────────────────────────────────────────────────────────────────
def bezier_pts(p0, p1, p2, p3, steps=18):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

def wave_points(y_center, scale):
    """Approximate one wave from the SVG logo."""
    # M8,yc C13,yc-5 17,yc-5 22,yc C27,yc+5 31,yc+5 36,yc C41,yc-5 45,yc-5 50,yc
    d  = 5 * scale
    sx = scale
    pts  = bezier_pts((8*sx, y_center), (13*sx, y_center-d), (17*sx, y_center-d), (22*sx, y_center))
    pts += bezier_pts((22*sx, y_center), (27*sx, y_center+d), (31*sx, y_center+d), (36*sx, y_center))
    pts += bezier_pts((36*sx, y_center), (41*sx, y_center-d), (45*sx, y_center-d), (50*sx, y_center))
    return [(int(x), int(y)) for x, y in pts]

def render_logo(target_w=300):
    """Render the Ola Digital logo as a PIL RGBA image."""
    svg_w, svg_h = 248, 68
    scale = target_w / svg_w
    lw    = int(svg_w * scale)
    lh    = int(svg_h * scale)

    img  = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Badge rounded rect
    badge_x2 = int(56 * scale)
    badge_y1 = int(4  * scale)
    badge_y2 = badge_y1 + int(56 * scale)
    rx       = int(14 * scale)
    draw.rounded_rectangle([(0, badge_y1), (badge_x2, badge_y2)],
                            radius=rx, fill=(255, 255, 255, 45),
                            outline=(255, 255, 255, 70), width=max(1, int(scale)))

    # Waves
    wave_defs = [
        (int(20 * scale), 100),
        (int(32 * scale), 180),
        (int(44 * scale), 255),
    ]
    for y_c, opacity in wave_defs:
        pts = wave_points(y_c, scale)
        if len(pts) > 1:
            draw.line(pts, fill=(255, 255, 255, opacity), width=max(2, int(2.2 * scale)))

    # "OLA" text
    ola_size = max(12, int(38 * scale))
    draw.text((int(68 * scale), int(42 * scale)), 'OLA',
              font=F(ola_size, 'black'), fill=(255, 255, 255, 255), anchor='lb')

    # "DIGITAL" spaced text
    dig_size = max(8, int(12 * scale))
    dig_font = F(dig_size, 'reg')
    dx = int(70 * scale)
    dy = int(57 * scale)
    for ch in 'DIGITAL':
        draw.text((dx, dy), ch, font=dig_font, fill=(255, 255, 255, 180), anchor='lb')
        dx += int((dig_size * 0.82) + 4 * scale)

    return img

LOGO = render_logo(300)


# ── Rendering ─────────────────────────────────────────────────────────────────
def blend_color(c, bg, a):
    return tuple(int(cv * a + bv * (1 - a)) for cv, bv in zip(c, bg))


def composite_logo(base_arr, alpha=1.0, margin=44):
    """Paste LOGO onto bottom-right of a numpy frame."""
    img  = Image.fromarray(base_arr)
    logo = LOGO.copy()
    if alpha < 1.0:
        r, g, b, a = logo.split()
        a = a.point(lambda x: int(x * alpha))
        logo = Image.merge('RGBA', (r, g, b, a))
    x = W - LOGO.width - margin
    y = H - LOGO.height - margin
    img.paste(logo, (x, y), logo)
    return np.array(img)


def render(elements, bg, with_logo=False, logo_alpha=1.0):
    img  = Image.new('RGB', (W, H), bg)
    draw = ImageDraw.Draw(img)

    for el in elements:
        if el.get('type') == 'sep':
            a = el.get('alpha', 1.0)
            c = blend_color(el.get('color', C_GREY), bg, a)
            y = el['y']
            draw.line([(80, y), (W - 80, y)], fill=c, width=2)
            continue

        if el.get('type') == 'rect':
            a = el.get('alpha', 1.0)
            c = blend_color(el['color'], bg, a)
            x1, y1, x2, y2 = el['rect']
            draw.rectangle([(x1, y1), (x2, y2)], fill=c)
            continue

        a = el.get('alpha', 1.0)
        if a <= 0.01:
            continue

        color  = blend_color(el['color'], bg, a)
        weight = el.get('weight', 'black')
        sz     = el.get('size', 80)

        # Zoom burst: re-render at scaled size
        zoom = el.get('zoom', 1.0)
        if zoom != 1.0:
            sz = max(10, int(sz * zoom))

        f      = F(sz, weight)
        align  = el.get('align', 'c')
        anchor = 'mm' if align == 'c' else ('lm' if align == 'l' else 'rm')
        draw.text((el['x'], el['y']), el['text'], font=f, fill=color, anchor=anchor)

    arr = np.array(img)
    if with_logo:
        arr = composite_logo(arr, logo_alpha)
    return arr


# ── Scene primitives ──────────────────────────────────────────────────────────
def clip(fn, dur): return VideoClip(fn, duration=dur).with_fps(FPS)


def scene_seq(lines, bg, dur, logo=False):
    """Lines fade + spring in one by one."""
    def mf(t):
        els = []
        for ln in lines:
            d = ln.get('delay', 0.0)
            if t < d:
                continue
            dt = t - d
            a  = min(1.0, dt / 0.3)
            y  = ln['y'] + spring(dt, 0.45)
            els.append({**ln, 'x': W // 2, 'align': 'c', 'y': y, 'alpha': a})
        la = min(1.0, (t - (dur - 0.8)) / 0.5) if logo else 0
        return render(els, bg, with_logo=logo, logo_alpha=max(0, la))
    return clip(mf, dur)


def scene_zoom_burst(lines, bg, dur):
    """Each line zooms from 130% to 100% on appearance — high-energy entrance."""
    def mf(t):
        els = []
        for ln in lines:
            d  = ln.get('delay', 0.0)
            if t < d:
                continue
            dt   = t - d
            a    = min(1.0, dt / 0.25)
            zd   = 0.35
            z    = zoom_scale(dt, zd) if dt < zd else 1.0
            els.append({**ln, 'x': W // 2, 'align': 'c', 'alpha': a, 'zoom': z})
        return render(els, bg)
    return clip(mf, dur)


def scene_word_stagger(sentence, y, base_size, color, bg, dur, delay=0.2, gap=0.16, weight='black'):
    """Each word bursts in separately — very dynamic feel."""
    words   = sentence.split()
    entries = [(w, delay + i * gap) for i, w in enumerate(words)]

    def mf(t):
        # Measure total width to center the line
        full_f = F(base_size, weight)
        total_w = sum(ImageFont.FreeTypeFont.getlength(full_f, w + ' ') for w in words)

        img  = Image.new('RGB', (W, H), bg)
        draw = ImageDraw.Draw(img)
        cursor = (W - total_w) / 2

        for word, wd in entries:
            if t < wd:
                ww = F(base_size, weight).getlength(word + ' ')
                cursor += ww
                continue
            dt = t - wd
            a  = min(1.0, dt / 0.22)
            z  = zoom_scale(dt, 0.3) if dt < 0.3 else 1.0
            sz = max(10, int(base_size * z))
            f  = F(sz, weight)
            c  = blend_color(color, bg, a)
            cy = y + spring(dt, 0.4, overshoot=18)
            draw.text((cursor, cy), word, font=f, fill=c, anchor='lm')
            cursor += F(base_size, weight).getlength(word + ' ')

        return np.array(img)
    return clip(mf, dur)


def scene_big_reveal(word, sub, bg, dur=5.0, word_color=None, sub_color=None):
    """One huge word slams in, subtitle fades below."""
    wc = word_color or C_TEAL
    sc = sub_color  or C_GREY

    def mf(t):
        els = []
        if t >= 0.0:
            z = zoom_scale(t, 0.4) if t < 0.4 else 1.0
            a = min(1.0, t / 0.2)
            els.append({'text': word, 'x': W//2, 'y': H//2 - 60,
                        'size': 200, 'color': wc, 'align': 'c', 'alpha': a, 'zoom': z, 'weight': 'black'})
        if t >= 0.6 and sub:
            a2 = min(1.0, (t - 0.6) / 0.35)
            y2 = H//2 + 100 + spring(t - 0.6, 0.45)
            els.append({'text': sub, 'x': W//2, 'y': y2,
                        'size': 64, 'color': sc, 'align': 'c', 'alpha': a2, 'weight': 'bold'})
        return render(els, bg)
    return clip(mf, dur)


def scene_counter(label_top, val_from, val_to, unit, color, bg, dur):
    """Huge count-up with pulse burst when it hits the final value."""
    def mf(t):
        a0 = min(1.0, t / 0.4)
        els = [{'text': label_top, 'x': W//2, 'y': 400,
                'size': 60, 'color': C_GREY, 'weight': 'bold', 'align': 'c', 'alpha': a0}]

        if t >= 0.6:
            p   = min(1.0, (t - 0.6) / (dur * 0.55))
            p   = 1 - (1 - p) ** 3
            val = int(val_from + (val_to - val_from) * p)
            a   = min(1.0, (t - 0.6) / 0.35)
            # Pulse when value hits target
            pulse_t = (dur * 0.55) + 0.6
            if t > pulse_t:
                zoom_t  = t - pulse_t
                z_extra = max(0, (1 - zoom_t / 0.4) * 0.12)
            else:
                z_extra = 0
            sz = int(280 * (1 + z_extra))
            els += [
                {'text': str(val), 'x': W//2, 'y': H//2 - 40,
                 'size': sz, 'color': color, 'align': 'c', 'alpha': a, 'weight': 'black'},
                {'text': unit, 'x': W//2, 'y': H//2 + 200,
                 'size': 58, 'color': C_WHITE, 'align': 'c', 'alpha': a, 'weight': 'bold'},
            ]
        return render(els, bg)
    return clip(mf, dur)


def scene_accent_lines(items, bg, dur, logo=False):
    """
    items: list of {text, size, color, y, delay, accent_color?}
    Draws a short colored bar BEFORE the text slides in.
    """
    def mf(t):
        els = []
        for item in items:
            d  = item.get('delay', 0.0)
            if t < d:
                continue
            dt = t - d
            # Accent bar sweeps in
            bar_a = min(1.0, dt / 0.15)
            acc_c = item.get('accent_color', C_TEAL)
            bar_w = int(smooth(dt, 0.2) * 80)
            els.append({'type': 'rect', 'color': acc_c, 'alpha': bar_a,
                        'rect': (W//2 - 40, item['y'] - item['size']//2 - 12,
                                 W//2 - 40 + bar_w, item['y'] - item['size']//2 - 7)})

            if dt >= 0.18:
                dt2 = dt - 0.18
                a   = min(1.0, dt2 / 0.28)
                y   = item['y'] + spring(dt2, 0.45)
                els.append({**item, 'x': W // 2, 'align': 'c', 'y': y, 'alpha': a})

        la = min(1.0, (t - (dur - 0.8)) / 0.5) if logo else 0
        return render(els, bg, with_logo=logo, logo_alpha=max(0, la))
    return clip(mf, dur)


def scene_split_counter(stats, bg, dur):
    """
    Multiple stats fade in staggered with accent lines.
    stats: [(delay, value_str, label, y)]
    """
    def mf(t):
        els = []
        for delay, val, label, y in stats:
            if t < delay:
                continue
            dt = t - delay
            a  = min(1.0, dt / 0.45)
            z  = zoom_scale(dt, 0.4) if dt < 0.4 else 1.0
            ys = y + spring(dt, 0.5)
            els += [
                {'text': val,   'x': W//2, 'y': ys,      'size': 130, 'color': C_TEAL,  'align': 'c', 'alpha': a, 'weight': 'black', 'zoom': z},
                {'text': label, 'x': W//2, 'y': ys + 90, 'size': 48,  'color': C_WHITE, 'align': 'c', 'alpha': a * 0.85, 'weight': 'bold'},
            ]
        return render(els, bg)
    return clip(mf, dur)


def scene_cta(headline, sub, bg=C_DARK):
    """Standard CTA with logo, headline, sub-line."""
    dur = 7.0
    def mf(t):
        els = []
        a0 = min(1.0, t / 0.35)
        y0 = H//2 - 130 + spring(t, 0.5)
        els.append({'text': headline, 'x': W//2, 'y': y0,
                    'size': 92, 'color': C_WHITE, 'align': 'c', 'alpha': a0, 'weight': 'black'})
        if t >= 0.5:
            a1 = min(1.0, (t - 0.5) / 0.35)
            y1 = H//2 + 30 + spring(t - 0.5, 0.5)
            els.append({'text': sub, 'x': W//2, 'y': y1,
                        'size': 68, 'color': C_TEAL, 'align': 'c', 'alpha': a1, 'weight': 'black'})
        if t >= 1.2:
            a2 = min(1.0, (t - 1.2) / 0.4)
            els.append({'text': 'Link en bio → WhatsApp', 'x': W//2, 'y': H//2 + 200,
                        'size': 54, 'color': C_GREY, 'align': 'c', 'alpha': a2, 'weight': 'bold'})
        la = min(1.0, (t - 0.4) / 0.6)
        return render(els, bg, with_logo=True, logo_alpha=max(0, la))
    return clip(mf, dur)


# ── Reel 6 — ¿Aparecés en Google? ────────────────────────────────────────────
def reel_6():
    scenes = []

    # Hook
    scenes.append(scene_zoom_burst([
        {'text': 'Hacé esto',    'size': 130, 'color': C_WHITE,  'y': H//2 - 120, 'delay': 0.0,  'weight': 'black'},
        {'text': 'ahora mismo.', 'size': 100, 'color': C_YELLOW, 'y': H//2 + 30,  'delay': 0.45, 'weight': 'black'},
    ], C_BLACK, 3.0))

    # Problem
    scenes.append(scene_accent_lines([
        {'text': 'Buscá tu negocio en Google.',  'size': 72, 'color': C_WHITE, 'y': H//2 - 200, 'delay': 0.2, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': '¿Aparece?',                    'size': 96, 'color': C_TEAL,  'y': H//2 - 20,  'delay': 0.9, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'Si no aparece,',               'size': 64, 'color': C_GREY,  'y': H//2 + 130, 'delay': 1.8, 'accent_color': C_RED,    'weight': 'bold'},
        {'text': 'no existís para quien te busca.', 'size': 60, 'color': C_RED, 'y': H//2 + 240, 'delay': 2.4, 'accent_color': C_RED,    'weight': 'bold'},
    ], C_DARK, 8.0))

    # Solution
    scenes.append(scene_accent_lines([
        {'text': 'Google My Business.',       'size': 90,  'color': C_WHITE,  'y': H//2 - 220, 'delay': 0.1, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'Gratis.',                   'size': 140, 'color': C_TEAL,   'y': H//2 - 50,  'delay': 0.7, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': '15 minutos en configurar.', 'size': 64,  'color': C_WHITE,  'y': H//2 + 130, 'delay': 1.5, 'accent_color': C_YELLOW, 'weight': 'bold'},
        {'text': 'Puede duplicar tus consultas.','size': 60,'color': C_GREY,  'y': H//2 + 250, 'delay': 2.2, 'accent_color': C_YELLOW, 'weight': 'bold'},
    ], C_DARK, 8.0))

    # Counter
    scenes.append(scene_counter(
        '+147% de visibilidad promedio', 0, 147, 'negocios que lo configuran bien', C_TEAL, C_DARK, 7.0
    ))

    # CTA
    scenes.append(scene_cta('¿Lo tenés activo?', 'Lo configuramos hoy.'))

    return concatenate_videoclips(scenes)


# ── Reel 7 — El Formato Que Más Crece ────────────────────────────────────────
def reel_7():
    scenes = []

    # Hook
    scenes.append(scene_word_stagger(
        'El formato que más alcance orgánico genera en Instagram 2026.',
        H // 2, 82, C_WHITE, C_BLACK, 4.5, delay=0.3, gap=0.14
    ))

    # Big reveal
    scenes.append(scene_big_reveal('CARRUSEL', 'El algoritmo lo favorece.', C_DARK))

    # Why
    scenes.append(scene_accent_lines([
        {'text': 'Los likes no importan tanto.', 'size': 72, 'color': C_WHITE, 'y': H//2 - 200, 'delay': 0.2, 'accent_color': C_GREY,  'weight': 'black'},
        {'text': 'Lo que importa:',              'size': 64, 'color': C_GREY,  'y': H//2 - 60,  'delay': 1.0, 'accent_color': C_TEAL,  'weight': 'bold'},
        {'text': 'GUARDADOS.',                   'size': 160,'color': C_TEAL,  'y': H//2 + 100, 'delay': 1.6, 'accent_color': C_TEAL,  'weight': 'black'},
    ], C_DARK, 7.0))

    # Explanation
    scenes.append(scene_zoom_burst([
        {'text': 'Cuando alguien guarda tu carrusel,', 'size': 66, 'color': C_WHITE,  'y': H//2 - 200, 'delay': 0.1,  'weight': 'black'},
        {'text': 'Instagram lo muestra',               'size': 76, 'color': C_WHITE,  'y': H//2 - 60,  'delay': 0.8,  'weight': 'black'},
        {'text': 'a más gente.',                       'size': 90, 'color': C_YELLOW, 'y': H//2 + 90,  'delay': 1.4,  'weight': 'black'},
    ], C_DARK, 7.0))

    # CTA
    scenes.append(scene_cta('¿Tenés uno?', 'Te lo armamos.'))

    return concatenate_videoclips(scenes)


# ── Reel 8 — Cuánto Vale Un Cliente ──────────────────────────────────────────
def reel_8():
    scenes = []

    # Hook
    scenes.append(scene_word_stagger(
        'Calculá esto y va a cambiar cómo invertís en marketing.',
        H // 2, 84, C_WHITE, C_BLACK, 4.0, delay=0.2, gap=0.12
    ))

    # Setup
    scenes.append(scene_accent_lines([
        {'text': '¿Cuánto gasta un cliente',    'size': 72, 'color': C_WHITE, 'y': H//2 - 200, 'delay': 0.2, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'en promedio por visita?',     'size': 72, 'color': C_WHITE, 'y': H//2 - 70,  'delay': 0.2, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': '¿Cuántas veces vuelve al año?','size': 64, 'color': C_GREY, 'y': H//2 + 90,  'delay': 1.2, 'accent_color': C_YELLOW, 'weight': 'bold'},
        {'text': 'Multiplicalo.',               'size': 90, 'color': C_TEAL,  'y': H//2 + 230, 'delay': 2.0, 'accent_color': C_TEAL,   'weight': 'black'},
    ], C_DARK, 8.0))

    # The math
    scenes.append(scene_zoom_burst([
        {'text': 'AR$ 5.000 por visita',      'size': 76, 'color': C_WHITE,  'y': H//2 - 240, 'delay': 0.1,  'weight': 'black'},
        {'text': '× 8 visitas al año',        'size': 76, 'color': C_WHITE,  'y': H//2 - 100, 'delay': 0.6,  'weight': 'black'},
        {'text': '=',                         'size': 110,'color': C_GREY,   'y': H//2 + 50,  'delay': 1.0,  'weight': 'black'},
        {'text': 'AR$ 40.000 por cliente',    'size': 84, 'color': C_YELLOW, 'y': H//2 + 200, 'delay': 1.3,  'weight': 'black'},
    ], C_DARK, 8.0))

    # The point
    scenes.append(scene_big_reveal('¿Cuánto', 'invertirías para conseguirlo?', C_DARK, word_color=C_TEAL))

    # CTA
    scenes.append(scene_cta('Nosotros lo calculamos.', 'Gratis. Sin compromiso.'))

    return concatenate_videoclips(scenes)


# ── Reel 9 — 3 Posts Que Todo Negocio Necesita ───────────────────────────────
def reel_9():
    scenes = []

    # Hook
    scenes.append(scene_zoom_burst([
        {'text': 'Si no sabés qué publicar,', 'size': 78,  'color': C_WHITE,  'y': H//2 - 100, 'delay': 0.0,  'weight': 'black'},
        {'text': 'empezá con estos 3.',        'size': 96,  'color': C_TEAL,   'y': H//2 + 70,  'delay': 0.5,  'weight': 'black'},
    ], C_BLACK, 3.0))

    # Post 1
    scenes.append(scene_accent_lines([
        {'text': '1.',         'size': 180, 'color': C_TEAL,  'y': H//2 - 200, 'delay': 0.1, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'TESTIMONIO', 'size': 110, 'color': C_WHITE, 'y': H//2 - 10,  'delay': 0.4, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'Prueba social > publicidad.','size': 60,'color': C_GREY,   'y': H//2 + 140, 'delay': 1.0, 'accent_color': C_GREY,  'weight': 'bold'},
    ], C_DARK, 5.0))

    # Post 2
    scenes.append(scene_accent_lines([
        {'text': '2.',         'size': 180, 'color': C_YELLOW,'y': H//2 - 200, 'delay': 0.1, 'accent_color': C_YELLOW, 'weight': 'black'},
        {'text': 'PROCESO',    'size': 110, 'color': C_WHITE, 'y': H//2 - 10,  'delay': 0.4, 'accent_color': C_YELLOW, 'weight': 'black'},
        {'text': 'Detrás de escena = confianza.','size': 60,'color': C_GREY, 'y': H//2 + 140, 'delay': 1.0, 'accent_color': C_GREY,  'weight': 'bold'},
    ], C_DARK, 5.0))

    # Post 3
    scenes.append(scene_accent_lines([
        {'text': '3.',         'size': 180, 'color': C_RED,   'y': H//2 - 200, 'delay': 0.1, 'accent_color': C_RED,    'weight': 'black'},
        {'text': 'OFERTA',     'size': 130, 'color': C_WHITE, 'y': H//2 - 10,  'delay': 0.4, 'accent_color': C_RED,    'weight': 'black'},
        {'text': '+ llamada a la acción.',  'size': 66,'color': C_RED,   'y': H//2 + 140, 'delay': 0.9, 'accent_color': C_RED,    'weight': 'bold'},
        {'text': 'Sin esto, el resto no sirve.','size': 56,'color': C_GREY, 'y': H//2 + 260, 'delay': 1.4, 'accent_color': C_GREY,  'weight': 'bold'},
    ], C_DARK, 6.0))

    # CTA
    scenes.append(scene_cta('¿Querés que los hagamos?', 'Por vos. Todos los meses.'))

    return concatenate_videoclips(scenes)


# ── Reel 10 — Tu Competencia Te Está Ganando ─────────────────────────────────
def reel_10():
    scenes = []

    # Hook — word stagger for maximum impact
    scenes.append(scene_word_stagger(
        'Hay un negocio igual al tuyo en Olavarría ganándote clientes ahora.',
        H // 2, 86, C_WHITE, C_BLACK, 4.5, delay=0.15, gap=0.13
    ))

    # Not better — just more visible
    scenes.append(scene_accent_lines([
        {'text': 'No porque sea mejor.',   'size': 86, 'color': C_WHITE, 'y': H//2 - 180, 'delay': 0.1, 'accent_color': C_GREY,  'weight': 'black'},
        {'text': 'Porque aparece',         'size': 90, 'color': C_TEAL,  'y': H//2 - 20,  'delay': 0.8, 'accent_color': C_TEAL,  'weight': 'black'},
        {'text': 'donde vos no estás.',    'size': 80, 'color': C_RED,   'y': H//2 + 130, 'delay': 1.4, 'accent_color': C_RED,   'weight': 'black'},
    ], C_DARK, 7.0))

    # The system
    scenes.append(scene_accent_lines([
        {'text': 'Instagram activo.',             'size': 76, 'color': C_WHITE, 'y': H//2 - 260, 'delay': 0.2, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'Google My Business.',           'size': 76, 'color': C_WHITE, 'y': H//2 - 120, 'delay': 0.9, 'accent_color': C_YELLOW, 'weight': 'black'},
        {'text': 'WhatsApp como CTA.',            'size': 76, 'color': C_WHITE, 'y': H//2 + 20,  'delay': 1.6, 'accent_color': C_TEAL,   'weight': 'black'},
        {'text': 'Ese es el sistema completo.',   'size': 58, 'color': C_GREY,  'y': H//2 + 170, 'delay': 2.4, 'accent_color': C_GREY,   'weight': 'bold'},
    ], C_DARK, 8.0))

    # Key insight
    scenes.append(scene_zoom_burst([
        {'text': 'No es complejo.',  'size': 104, 'color': C_WHITE, 'y': H//2 - 90, 'delay': 0.1, 'weight': 'black'},
        {'text': 'Es consistente.',  'size': 104, 'color': C_TEAL,  'y': H//2 + 70, 'delay': 0.6, 'weight': 'black'},
    ], C_DARK, 5.0))

    # CTA
    scenes.append(scene_cta('Podés empezar hoy.', 'Ola Digital — Olavarría.'))

    return concatenate_videoclips(scenes)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)

    reels = [
        ('reel_6_google_my_business.mp4',  reel_6),
        ('reel_7_formato_carrusel.mp4',     reel_7),
        ('reel_8_cuanto_vale_cliente.mp4',  reel_8),
        ('reel_9_tres_posts.mp4',           reel_9),
        ('reel_10_competencia.mp4',         reel_10),
    ]

    for filename, builder in reels:
        path = os.path.join(OUT, filename)
        print(f'\nGenerando {filename}...')
        video = builder()
        video.write_videofile(
            path, fps=FPS, codec='libx264',
            audio=False, logger=None,
            ffmpeg_params=['-crf', '23', '-preset', 'fast']
        )
        print(f'  OK → {path}')

    print('\nListo. Reels 6–10 en .tmp/reels/')
