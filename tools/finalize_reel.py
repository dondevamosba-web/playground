#!/usr/bin/env python3
"""
Finalize a reel for Instagram:
  1. Generate a royalty-free trap/modern beat
  2. Add WhatsApp CTA text overlay on the last scene
  3. Merge audio + video → final MP4
"""

import os, sys
import numpy as np
from scipy.io import wavfile
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, VideoClip, CompositeVideoClip, concatenate_videoclips

RATE   = 44100
BPM    = 92
BEAT   = 60.0 / BPM
W, H   = 1080, 1920
FPS    = 30

FONT_PATH = '/System/Library/Fonts/HelveticaNeue.ttc'
IDX_BLACK = 9
IDX_BOLD  = 1

C_DARK  = (13,  27,  42)
C_TEAL  = (46,  196, 182)
C_WHITE = (255, 255, 255)
C_GREY  = (140, 150, 165)

BASE  = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'reels')
SRC   = os.path.join(BASE, 'reel_10_competencia.mp4')
BEAT_WAV = os.path.join(BASE, 'beat.wav')
OUT   = os.path.join(BASE, 'reel_10_final.mp4')


# ── Beat generator ────────────────────────────────────────────────────────────

def env(t, attack=0.002, decay=0.12, sus=0.0):
    a = np.minimum(t / attack, 1.0)
    d = np.maximum(1.0 - (t - attack) / decay, sus)
    return a * np.where(t < attack, 1.0, d)

def make_kick(dur=0.35):
    n  = int(RATE * dur)
    t  = np.linspace(0, dur, n)
    f  = 180 * np.exp(-22 * t) + 40          # pitch drop: 180→40 Hz
    ph = 2 * np.pi * np.cumsum(f) / RATE
    e  = np.exp(-18 * t) * 1.1
    return np.clip(e * np.sin(ph), -1, 1).astype(np.float32)

def make_snare(dur=0.18):
    n     = int(RATE * dur)
    t     = np.linspace(0, dur, n)
    noise = np.random.default_rng(42).uniform(-1, 1, n).astype(np.float32)
    tone  = 0.4 * np.sin(2 * np.pi * 240 * t)
    e     = np.exp(-28 * t)
    return (e * (0.65 * noise + tone) * 0.7).astype(np.float32)

def make_hihat(dur=0.04, amp=0.18):
    n     = int(RATE * dur)
    t     = np.linspace(0, dur, n)
    noise = np.random.default_rng(7).uniform(-1, 1, n).astype(np.float32)
    e     = np.exp(-60 * t)
    return (e * noise * amp).astype(np.float32)

def make_open_hat(dur=0.12, amp=0.14):
    n     = int(RATE * dur)
    t     = np.linspace(0, dur, n)
    noise = np.random.default_rng(11).uniform(-1, 1, n).astype(np.float32)
    e     = np.exp(-18 * t)
    return (e * noise * amp).astype(np.float32)

def make_sub_bass(freq, dur):
    n = int(RATE * dur)
    t = np.linspace(0, dur, n)
    e = np.exp(-3.5 * t) * 0.6 + 0.1
    return (e * np.sin(2 * np.pi * freq * t) * 0.55).astype(np.float32)

def make_synth_pad(freqs, dur, amp=0.12):
    """Simple chord pad — multiple detuned sines."""
    n   = int(RATE * dur)
    t   = np.linspace(0, dur, n)
    out = np.zeros(n, dtype=np.float32)
    e   = (1 - np.exp(-4 * t)) * np.exp(-1.5 * t) + 0.15
    for f in freqs:
        for detune in [-2, 0, 2]:
            out += np.sin(2 * np.pi * (f + detune) * t) * amp / 3
    return (out * e).astype(np.float32)


def add_at(buf, sample, pos):
    end = min(pos + len(sample), len(buf))
    buf[pos:end] += sample[:end - pos]


def generate_beat(duration):
    total   = int(RATE * duration)
    audio   = np.zeros(total, dtype=np.float32)

    kick    = make_kick()
    snare   = make_snare()
    hihat   = make_hihat()
    openhat = make_open_hat()

    # Bass note sequence (Hz) per bar
    bass_seq = [55, 55, 49, 52, 55, 55, 49, 44]

    bars = int(duration / (4 * BEAT)) + 2
    for bar in range(bars):
        base = bar * 4 * BEAT

        # Kick: beats 1, 1.5 (trap double), 3
        for b in [0.0, 0.5, 2.0]:
            add_at(audio, kick, int((base + b) * BEAT * RATE))

        # Snare: beats 2 and 4
        for b in [1.0, 3.0]:
            add_at(audio, snare, int((base + b) * BEAT * RATE))

        # Hi-hats: 16th notes with velocity variation
        for step in range(16):
            amp   = 0.22 if step % 2 == 0 else 0.13
            hat   = make_hihat(amp=amp)
            ohat  = openhat if step in (6, 14) else None
            pos   = int((base + step * 0.25) * BEAT * RATE)
            add_at(audio, hat, pos)
            if ohat is not None:
                add_at(audio, ohat, pos)

        # Sub bass
        note_idx  = bar % len(bass_seq)
        bass_freq = bass_seq[note_idx]
        bass_note = make_sub_bass(bass_freq, BEAT * 3.8)
        add_at(audio, bass_note, int(base * BEAT * RATE))

        # Synth pad every 2 bars (whole note)
        if bar % 2 == 0:
            root = bass_seq[note_idx]
            pad  = make_synth_pad([root * 2, root * 2.5, root * 3], BEAT * 7.8)
            add_at(audio, pad, int(base * BEAT * RATE))

    # Fade out last 2 seconds
    fade_start = int((duration - 2.0) * RATE)
    if fade_start < total:
        fade = np.linspace(1, 0, total - fade_start)
        audio[fade_start:] *= fade

    # Normalize
    peak  = np.max(np.abs(audio))
    audio = audio / (peak + 1e-6) * 0.82
    return (audio * 32767).astype(np.int16)


# ── WhatsApp CTA overlay ──────────────────────────────────────────────────────

def smooth(t, dur):
    p = min(1.0, max(0.0, t / dur)) if dur > 0 else 1.0
    return p * p * (3 - 2 * p)

def blend(c, bg, a):
    return tuple(int(cv * a + bv * (1 - a)) for cv, bv in zip(c, bg))

def render_cta_overlay(t, total_dur, wa_number='5491162310105'):
    """
    Renders the WA CTA box. Fades in over 0.4s, fades out last 0.3s.
    Positioned at bottom ~20% of frame.
    """
    img  = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fade in/out alpha
    if t < 0.4:
        alpha = smooth(t, 0.4)
    elif t > total_dur - 0.3:
        alpha = smooth(total_dur - t, 0.3)
    else:
        alpha = 1.0

    box_h = 210
    box_y = H - box_h - 80
    box_alpha = int(220 * alpha)

    # Pill background
    draw.rounded_rectangle(
        [(60, box_y), (W - 60, box_y + box_h)],
        radius=24,
        fill=(46, 196, 182, box_alpha)
    )

    # WhatsApp icon dots (simple "W" style indicator)
    dot_c = (13, 27, 42, int(200 * alpha))
    for dx in [100, 120, 140]:
        draw.ellipse([(dx - 5, box_y + 18), (dx + 5, box_y + 28)], fill=dot_c)

    # "¿Hablamos?" line
    f1  = ImageFont.truetype(FONT_PATH, 58, index=IDX_BLACK)
    c1  = blend(C_DARK, (46, 196, 182), alpha)
    draw.text((W // 2, box_y + 68), '¿Hablamos?', font=f1, fill=c1, anchor='mm')

    # WA link line
    f2  = ImageFont.truetype(FONT_PATH, 44, index=IDX_BOLD)
    c2  = blend((13, 27, 42), (46, 196, 182), alpha * 0.75)
    draw.text((W // 2, box_y + 148), f'wa.me/{wa_number}', font=f2, fill=c2, anchor='mm')

    return img


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    # 1. Generate beat
    print('Generando beat...')
    video_clip = VideoFileClip(SRC)
    duration   = video_clip.duration
    video_clip.close()

    beat_data  = generate_beat(duration + 0.5)
    wavfile.write(BEAT_WAV, RATE, beat_data)
    print(f'  Beat generado: {duration:.1f}s @ {BPM} BPM')

    # 2. Build the WA overlay clip (appears at t = duration - 7s)
    print('Agregando overlay de WhatsApp...')
    overlay_start = max(0, duration - 7.0)
    overlay_dur   = duration - overlay_start

    def make_overlay_frame(t):
        frame = render_cta_overlay(t, overlay_dur)
        return np.array(frame)

    overlay_clip = (
        VideoClip(make_overlay_frame, duration=overlay_dur, is_mask=False)
        .with_fps(FPS)
        .with_start(overlay_start)
    )
    # RGBA → need to handle transparency via mask
    # Simpler: composite with PIL directly by re-rendering base + overlay
    # We'll use a different approach: render the overlay as RGBA and paste

    # 3. Load source video, composite overlay
    src_clip = VideoFileClip(SRC)

    def make_composited_frame(t):
        base_frame = src_clip.get_frame(t)
        if t < overlay_start:
            return base_frame
        overlay_t   = t - overlay_start
        base_img    = Image.fromarray(base_frame)
        overlay_img = render_cta_overlay(overlay_t, overlay_dur)
        base_img.paste(overlay_img, (0, 0), overlay_img)
        return np.array(base_img)

    composited = VideoClip(make_composited_frame, duration=duration).with_fps(FPS)

    # 4. Attach audio
    print('Mergeando audio...')
    audio_clip  = AudioFileClip(BEAT_WAV).with_duration(duration)
    final_clip  = composited.with_audio(audio_clip)

    # 5. Export
    print(f'Exportando → {OUT}')
    final_clip.write_videofile(
        OUT, fps=FPS, codec='libx264', audio_codec='aac',
        logger=None, ffmpeg_params=['-crf', '22', '-preset', 'fast']
    )

    src_clip.close()
    audio_clip.close()
    print(f'\nListo: {OUT}')


if __name__ == '__main__':
    main()
