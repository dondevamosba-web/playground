#!/usr/bin/env python3
"""
Ola Digital — Reel Generator
Produces 5 Instagram Reels (1080x1920) using kinetic typography.
No camera footage required. Output: .tmp/reels/
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, concatenate_videoclips

W, H   = 1080, 1920
FPS    = 30
OUT    = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'reels')

# Brand palette
C_BLACK  = (0,   0,   0)
C_DARK   = (13,  27,  42)
C_TEAL   = (46,  196, 182)
C_RED    = (230, 57,  70)
C_YELLOW = (255, 209, 102)
C_WHITE  = (255, 255, 255)
C_GREY   = (155, 155, 165)

FONT     = '/System/Library/Fonts/HelveticaNeue.ttc'


# ── Helpers ──────────────────────────────────────────────────────────────────

def font(size):
    return ImageFont.truetype(FONT, size)


def smoothstep(t, duration):
    p = min(1.0, max(0.0, t / duration)) if duration > 0 else 1.0
    return p * p * (3 - 2 * p)


def blend(color, bg, alpha):
    return tuple(int(c * alpha + b * (1 - alpha)) for c, b in zip(color, bg))


def render(elements, bg):
    """
    Draw a frame. Each element dict keys:
      text, x, y, size, color, align ('c'|'l'), alpha
    Special: type='sep' draws a horizontal line.
    """
    img = Image.new('RGB', (W, H), bg)
    d   = ImageDraw.Draw(img)

    for el in elements:
        if el.get('type') == 'sep':
            a = el.get('alpha', 1.0)
            c = blend(el.get('color', C_GREY), bg, a)
            y = el['y']
            d.line([(100, y), (W - 100, y)], fill=c, width=2)
            continue

        alpha = el.get('alpha', 1.0)
        if alpha <= 0:
            continue
        color = blend(el['color'], bg, alpha)
        f     = font(el['size'])
        align = el.get('align', 'c')
        anchor = 'mm' if align == 'c' else 'lm'
        d.text((el['x'], el['y']), el['text'], font=f, fill=color, anchor=anchor)

    return np.array(img)


# ── Scene primitives ──────────────────────────────────────────────────────────

def clip(make_frame_fn, duration):
    return VideoClip(make_frame_fn, duration=duration).with_fps(FPS)


def scene_seq(lines, bg, duration):
    """Lines appear one by one. Each line: {text, size, color, y, delay, align?}"""
    def mf(t):
        els = []
        for ln in lines:
            d = ln.get('delay', 0)
            if t >= d:
                a = smoothstep(t - d, 0.35)
                els.append({**ln, 'x': W // 2, 'align': ln.get('align', 'c'), 'alpha': a})
        return render(els, bg)
    return clip(mf, duration)


def scene_typewriter(text, y, size, color, bg, duration, start=0.4):
    n    = len(text)
    step = max(0.04, (duration - start) / n) if n else 0.05

    def mf(t):
        chars = 0 if t < start else min(n, int((t - start) / step) + 1)
        el = {'text': text[:chars], 'x': W // 2, 'y': y, 'size': size,
              'color': color, 'align': 'c', 'alpha': 1.0}
        return render([el], bg)
    return clip(mf, duration)


def scene_static(elements, bg, duration, fade=0.4):
    def mf(t):
        a   = smoothstep(t, fade)
        els = [{**e, 'alpha': e.get('alpha', 1.0) * a} for e in elements]
        return render(els, bg)
    return clip(mf, duration)


def scene_slide_up(lines, bg, duration):
    def mf(t):
        els = []
        for ln in lines:
            d = ln.get('delay', 0)
            if t >= d:
                p      = smoothstep(t - d, 0.45)
                offset = int((1 - p) * 130)
                els.append({**ln, 'x': W // 2, 'align': 'c',
                             'y': ln['y'] + offset, 'alpha': p})
        return render(els, bg)
    return clip(mf, duration)


# ── Reel 1 — Antes y Después ──────────────────────────────────────────────────

def reel_1():
    scenes = []

    # Hook
    scenes.append(scene_seq([
        {'text': 'Este restaurante de Olavarría', 'size': 66, 'color': C_WHITE,  'y': H//2 - 90,  'delay': 0.1},
        {'text': 'casi cierra en enero.',          'size': 72, 'color': C_TEAL,   'y': H//2 + 50,  'delay': 0.8},
    ], C_BLACK, 3.0))

    # Problema
    scenes.append(scene_seq([
        {'text': '8 reservas por semana.',               'size': 68, 'color': C_RED,   'y': H//2 - 160, 'delay': 0.2},
        {'text': 'Local vacío de lunes a jueves.',        'size': 58, 'color': C_WHITE, 'y': H//2 - 10,  'delay': 1.4},
        {'text': 'Dueño poniendo plata de su bolsillo.', 'size': 52, 'color': C_GREY,  'y': H//2 + 140, 'delay': 2.6},
    ], C_DARK, 7.0))

    # Intervención
    scenes.append(scene_seq([
        {'text': 'Arrancamos con Meta Ads.',    'size': 66, 'color': C_WHITE, 'y': H//2 - 180, 'delay': 0.2},
        {'text': 'AR$ 80.000 / mes.',           'size': 84, 'color': C_TEAL,  'y': H//2 - 30,  'delay': 1.2},
        {'text': 'Radio 15km de Olavarría.',    'size': 56, 'color': C_GREY,  'y': H//2 + 120, 'delay': 2.3},
    ], C_DARK, 8.0))

    # Resultado con contador
    def result(t):
        els = []
        a0  = smoothstep(t, 0.4)
        els.append({'text': '45 días después.', 'x': W//2, 'y': 420,
                    'size': 58, 'color': C_GREY, 'align': 'c', 'alpha': a0})

        if t >= 0.8:
            p   = smoothstep(t - 0.8, 3.5)
            val = int(8 + (34 - 8) * (1 - (1 - p) ** 2))
            a   = smoothstep(t - 0.8, 0.4)
            els += [
                {'text': str(val),             'x': W//2, 'y': H//2 - 60,  'size': 300, 'color': C_TEAL,  'align': 'c', 'alpha': a},
                {'text': 'reservas / semana',  'x': W//2, 'y': H//2 + 200, 'size': 52,  'color': C_WHITE, 'align': 'c', 'alpha': a},
            ]
        if t >= 5.0:
            a2 = smoothstep(t - 5.0, 0.4)
            els.append({'text': 'Local lleno jue · vie · sáb.',
                        'x': W//2, 'y': H - 320, 'size': 54, 'color': C_YELLOW, 'align': 'c', 'alpha': a2})
        return render(els, C_DARK)

    scenes.append(clip(result, 10.0))

    # CTA
    scenes.append(scene_seq([
        {'text': '¿Tenés un negocio en Olavarría',  'size': 56, 'color': C_GREY,  'y': H//2 - 200, 'delay': 0.2},
        {'text': 'que necesita más clientes?',       'size': 66, 'color': C_WHITE, 'y': H//2 - 70,  'delay': 0.2},
        {'text': 'Link en bio',                      'size': 84, 'color': C_TEAL,  'y': H//2 + 120, 'delay': 1.2},
        {'text': 'hablemos por WhatsApp',             'size': 52, 'color': C_GREY,  'y': H//2 + 250, 'delay': 1.9},
        {'text': 'Ola Digital',                      'size': 48, 'color': C_WHITE, 'y': H - 200,    'delay': 2.6},
    ], C_DARK, 10.0))

    return concatenate_videoclips(scenes)


# ── Reel 2 — El Error Más Caro ────────────────────────────────────────────────

def reel_2():
    scenes = []

    # Hook
    scenes.append(scene_seq([
        {'text': 'Tus posts tienen likes.',    'size': 68, 'color': C_WHITE,  'y': H//2 - 120, 'delay': 0.1},
        {'text': 'Pero no tenés clientes.',   'size': 76, 'color': C_WHITE,  'y': H//2 + 20,  'delay': 0.7},
        {'text': '¿Por qué?',                 'size': 96, 'color': C_YELLOW, 'y': H//2 + 170, 'delay': 1.4},
    ], C_BLACK, 3.0))

    # El error — split idea
    def error_frame(t):
        els = []
        a1  = smoothstep(t, 0.4)
        els += [
            {'text': 'Estás publicando para',  'x': W//2, 'y': H//2 - 200, 'size': 58, 'color': C_GREY,  'align': 'c', 'alpha': a1},
            {'text': 'conseguir likes.',        'x': W//2, 'y': H//2 - 70,  'size': 90, 'color': C_RED,   'align': 'c', 'alpha': a1},
        ]
        if t >= 5.0:
            a2 = smoothstep(t - 5.0, 0.35)
            els.append({'type': 'sep', 'y': H//2 + 30, 'color': C_GREY, 'alpha': a2})
        if t >= 5.5:
            a3 = smoothstep(t - 5.5, 0.4)
            els += [
                {'text': 'Deberías publicar para', 'x': W//2, 'y': H//2 + 120, 'size': 58, 'color': C_GREY, 'align': 'c', 'alpha': a3},
                {'text': 'conseguir clientes.',    'x': W//2, 'y': H//2 + 255, 'size': 84, 'color': C_TEAL, 'align': 'c', 'alpha': a3},
            ]
        return render(els, C_DARK)

    scenes.append(clip(error_frame, 11.0))

    # Por qué pasa
    scenes.append(scene_seq([
        {'text': 'Un post sin llamada a la acción', 'size': 58, 'color': C_WHITE, 'y': H//2 - 140, 'delay': 0.2},
        {'text': 'es entretenimiento gratis',        'size': 70, 'color': C_RED,   'y': H//2,       'delay': 1.2},
        {'text': 'para tu competencia.',             'size': 58, 'color': C_WHITE, 'y': H//2 + 130, 'delay': 2.2},
    ], C_DARK, 8.0))

    # Solución
    scenes.append(scene_seq([
        {'text': 'La solución es simple:',      'size': 52, 'color': C_GREY,  'y': H//2 - 280, 'delay': 0.2},
        {'text': 'Cada post necesita',          'size': 64, 'color': C_WHITE, 'y': H//2 - 140, 'delay': 0.5},
        {'text': 'una acción clara.',           'size': 76, 'color': C_TEAL,  'y': H//2 - 10,  'delay': 0.5},
        {'text': '"Escribinos por WhatsApp"',   'size': 50, 'color': C_WHITE, 'y': H//2 + 130, 'delay': 1.5},
        {'text': '"Reservá" · "Pedí tu turno"', 'size': 48, 'color': C_WHITE, 'y': H//2 + 240, 'delay': 2.2},
    ], C_DARK, 7.0))

    # CTA
    scenes.append(scene_static([
        {'text': 'Ola Digital',  'x': W//2, 'y': H//2 - 70, 'size': 96, 'color': C_WHITE, 'align': 'c'},
        {'text': 'Link en bio',  'x': W//2, 'y': H//2 + 90, 'size': 68, 'color': C_TEAL,  'align': 'c'},
    ], C_DARK, 3.0))

    return concatenate_videoclips(scenes)


# ── Reel 3 — Así Funciona ─────────────────────────────────────────────────────

def reel_3():
    scenes = []

    # Hook
    scenes.append(scene_seq([
        {'text': 'Así consiguió esta clínica dental', 'size': 58, 'color': C_WHITE, 'y': H//2 - 160, 'delay': 0.1},
        {'text': '18 pacientes nuevos',               'size': 98, 'color': C_TEAL,  'y': H//2,       'delay': 0.6},
        {'text': 'en 30 días.',                       'size': 72, 'color': C_WHITE, 'y': H//2 + 140, 'delay': 1.2},
    ], C_BLACK, 3.0))

    # Punto de partida
    scenes.append(scene_seq([
        {'text': 'La clínica: zona centro, Olavarría.', 'size': 54, 'color': C_WHITE, 'y': H//2 - 200, 'delay': 0.2},
        {'text': 'Agenda con huecos.',                   'size': 74, 'color': C_RED,   'y': H//2 - 50,  'delay': 1.2},
        {'text': 'Sin captación digital.',               'size': 60, 'color': C_GREY,  'y': H//2 + 90,  'delay': 2.0},
        {'text': 'Inversión en ads: AR$ 0.',             'size': 56, 'color': C_GREY,  'y': H//2 + 210, 'delay': 3.0},
    ], C_DARK, 7.0))

    # 3 pasos
    pasos = [
        (5.0, [
            {'text': 'Paso 1',                       'size': 52, 'color': C_TEAL,  'y': H//2 - 220, 'delay': 0.2},
            {'text': 'Audiencia: mujeres y hombres', 'size': 58, 'color': C_WHITE, 'y': H//2 - 80,  'delay': 0.5},
            {'text': '25–55 años · radio 10km',      'size': 58, 'color': C_WHITE, 'y': H//2 + 50,  'delay': 0.5},
            {'text': 'de la clínica.',               'size': 58, 'color': C_GREY,  'y': H//2 + 170, 'delay': 0.9},
        ]),
        (4.0, [
            {'text': 'Paso 2',                       'size': 52, 'color': C_TEAL,  'y': H//2 - 220, 'delay': 0.1},
            {'text': '"¿Hace cuánto no vas',         'size': 64, 'color': C_WHITE, 'y': H//2 - 60,  'delay': 0.4},
            {'text': 'al dentista?"',                'size': 64, 'color': C_YELLOW,'y': H//2 + 70,  'delay': 0.4},
            {'text': 'CTA directo a WhatsApp',       'size': 50, 'color': C_GREY,  'y': H//2 + 200, 'delay': 1.0},
        ]),
        (5.0, [
            {'text': 'Paso 3',               'size': 52, 'color': C_TEAL,  'y': H//2 - 220, 'delay': 0.1},
            {'text': 'Presupuesto:',         'size': 60, 'color': C_WHITE, 'y': H//2 - 60,  'delay': 0.4},
            {'text': 'AR$ 120.000 / mes',    'size': 86, 'color': C_TEAL,  'y': H//2 + 90,  'delay': 0.7},
        ]),
    ]
    for dur, lines in pasos:
        scenes.append(scene_seq(lines, C_DARK, dur))

    # WOW — resultado
    stats = [
        (1.0,  '823',   'personas alcanzadas por día', 560),
        (3.0,  '47',    'consultas por WhatsApp',       880),
        (5.5,  '18',    'pacientes nuevos',             1200),
        (7.5,  '6.666', 'costo por paciente (AR$)',     1520),
    ]

    def wow(t):
        els = []
        a0  = smoothstep(t, 0.4)
        els.append({'text': '30 días después.', 'x': W//2, 'y': 360,
                    'size': 58, 'color': C_GREY, 'align': 'c', 'alpha': a0})
        for delay, val, label, y in stats:
            if t >= delay:
                a = smoothstep(t - delay, 0.5)
                els += [
                    {'text': val,   'x': W//2, 'y': y,      'size': 110, 'color': C_TEAL,  'align': 'c', 'alpha': a},
                    {'text': label, 'x': W//2, 'y': y + 80, 'size': 44,  'color': C_WHITE, 'align': 'c', 'alpha': a},
                ]
        return render(els, C_DARK)

    scenes.append(clip(wow, 11.0))

    # CTA
    scenes.append(scene_seq([
        {'text': '¿Tenés una clínica o consultorio',  'size': 60, 'color': C_WHITE, 'y': H//2 - 200, 'delay': 0.2},
        {'text': 'en Olavarría?',                     'size': 60, 'color': C_WHITE, 'y': H//2 - 80,  'delay': 0.2},
        {'text': 'Hacemos lo mismo para vos.',        'size': 66, 'color': C_TEAL,  'y': H//2 + 80,  'delay': 1.0},
        {'text': 'WhatsApp en bio',                   'size': 74, 'color': C_YELLOW,'y': H//2 + 230, 'delay': 1.8},
        {'text': 'Ola Digital',                       'size': 50, 'color': C_GREY,  'y': H - 200,    'delay': 2.5},
    ], C_DARK, 7.0))

    return concatenate_videoclips(scenes)


# ── Reel 4 — Pregunta de la Semana ───────────────────────────────────────────

def reel_4():
    scenes = []

    scenes.append(scene_typewriter(
        'Si tenés un negocio en Olavarría...',
        H // 2, 68, C_WHITE, C_DARK, 4.0, start=0.5
    ))

    scenes.append(scene_seq([
        {'text': '¿Sabés cuánto te cuesta',    'size': 84, 'color': C_WHITE,  'y': H//2 - 90, 'delay': 0.2},
        {'text': 'conseguir un cliente nuevo?','size': 82, 'color': C_YELLOW, 'y': H//2 + 70, 'delay': 0.7},
    ], C_DARK, 9.0))

    scenes.append(scene_slide_up([
        {'text': 'Respondé en los comentarios', 'y': H//2 - 40,  'size': 72, 'color': C_TEAL,  'delay': 0.1},
        {'text': 'Ola Digital',                 'y': H//2 + 110, 'size': 50, 'color': C_GREY,  'delay': 0.5},
    ], C_DARK, 3.0))

    return concatenate_videoclips(scenes)


# ── Reel 5 — Caso Local Spotlight ────────────────────────────────────────────

def reel_5():
    scenes = []

    # Hook
    scenes.append(scene_seq([
        {'text': 'Cómo este gym de Olavarría', 'size': 64, 'color': C_WHITE, 'y': H//2 - 140, 'delay': 0.1},
        {'text': 'duplicó sus consultas',       'size': 84, 'color': C_TEAL,  'y': H//2,       'delay': 0.6},
        {'text': 'en 30 días.',                 'size': 70, 'color': C_WHITE, 'y': H//2 + 130, 'delay': 1.1},
    ], C_BLACK, 3.0))

    # Punto de partida
    scenes.append(scene_seq([
        {'text': 'Enero.',                          'size': 104,'color': C_RED,   'y': H//2 - 220, 'delay': 0.2},
        {'text': 'Poca gente. Consultas estancadas.','size': 56, 'color': C_WHITE, 'y': H//2 - 60,  'delay': 1.0},
        {'text': 'El gym: bueno.',                  'size': 62, 'color': C_GREY,  'y': H//2 + 80,  'delay': 2.2},
        {'text': 'La visibilidad: casi cero.',      'size': 62, 'color': C_RED,   'y': H//2 + 200, 'delay': 3.2},
    ], C_DARK, 8.0))

    # La táctica
    scenes.append(scene_seq([
        {'text': 'La táctica:',              'size': 58, 'color': C_GREY,  'y': H//2 - 320, 'delay': 0.2},
        {'text': 'Stories todos los días.',  'size': 78, 'color': C_TEAL,  'y': H//2 - 160, 'delay': 0.6},
        {'text': '30 días. Sin excepción.',  'size': 66, 'color': C_WHITE, 'y': H//2 - 20,  'delay': 1.4},
        {'text': 'Clase del día. Progreso.', 'size': 52, 'color': C_GREY,  'y': H//2 + 120, 'delay': 2.5},
        {'text': 'Tips. Detrás de escena.',  'size': 52, 'color': C_GREY,  'y': H//2 + 230, 'delay': 3.2},
    ], C_DARK, 11.0))

    # Resultado
    results = [
        (0.8,  'x2',    'consultas por DM',      640),
        (3.0,  '11',    'socios nuevos ese mes', 1000),
        (5.5,  'AR$ 0', 'de inversión extra',    1360),
    ]

    def result(t):
        els = []
        a0  = smoothstep(t, 0.4)
        els.append({'text': '30 días después.', 'x': W//2, 'y': 360,
                    'size': 58, 'color': C_GREY, 'align': 'c', 'alpha': a0})
        for delay, val, label, y in results:
            if t >= delay:
                a = smoothstep(t - delay, 0.5)
                els += [
                    {'text': val,   'x': W//2, 'y': y,      'size': 130, 'color': C_TEAL,  'align': 'c', 'alpha': a},
                    {'text': label, 'x': W//2, 'y': y + 90, 'size': 46,  'color': C_WHITE, 'align': 'c', 'alpha': a},
                ]
        return render(els, C_DARK)

    scenes.append(clip(result, 9.0))

    # Cierre
    scenes.append(scene_seq([
        {'text': 'Olavarría hace bien las cosas.', 'size': 60, 'color': C_WHITE, 'y': H//2 - 120, 'delay': 0.2},
        {'text': 'Un tip de',                       'size': 50, 'color': C_GREY,  'y': H//2 + 60,  'delay': 1.2},
        {'text': 'Ola Digital',                     'size': 86, 'color': C_TEAL,  'y': H//2 + 200, 'delay': 1.5},
    ], C_DARK, 5.0))

    return concatenate_videoclips(scenes)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)

    reels = [
        ('reel_1_antes_y_despues.mp4',  reel_1),
        ('reel_2_el_error_mas_caro.mp4', reel_2),
        ('reel_3_asi_funciona.mp4',      reel_3),
        ('reel_4_pregunta.mp4',          reel_4),
        ('reel_5_spotlight.mp4',         reel_5),
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

    print('\nListo. Los 5 Reels están en .tmp/reels/')
