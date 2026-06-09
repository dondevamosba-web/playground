"""
Generates OLA Digital logo variants using Claude (Anthropic API via claude_call.py).
Produces polished SVG files — vector, scalable, professional quality.
Outputs: website/assets/logo-*.svg and brand-toolkit/assets/logo-*.svg
Usage: python3 tools/generate_logo_ai.py
"""

import json
import sys
from pathlib import Path

ROOT    = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from claude_call import call_claude

ASSETS  = ROOT / "website" / "assets"
TOOLKIT = ROOT / "brand-toolkit" / "assets"

BRAND_BRIEF = """
Brand: OLA Digital
Type: Digital marketing agency, Olavarría, Buenos Aires, Argentina
Meaning: "OLA" = wave in Spanish — connects to ocean, momentum, energy
Colors: deep ocean blue #0C4A6E, sky blue #0EA5E9, bright cyan #06B6D4, teal #38BDF8, orange accent #F97316
Fonts in SVG: Plus Jakarta Sans (bold/extrabold for OLA), Inter (regular/medium for DIGITAL)
Style: Modern, minimal, flat, professional — think Vercel, Linear, Stripe brand aesthetics
"""

LOGO_TASKS = [
    # ── B6-inspired: dark backgrounds, gradients, glow, dramatic ──────────────

    {
        "name": "logo-c1",
        "label": "Dark + horizon line — OLA sunset gradient, thin cyan horizon",
        "prompt": f"""
{BRAND_BRIEF}

Design a dark logo inspired by this style: dark bg, perspective grid, OLA in orange-pink gradient with glow, DIGITAL in cyan below.

This variant:
- Background rect 300×80, fill #050A14 (deep dark blue-black)
- A single bold horizon line at y=60, full width, stroke #38BDF8, stroke-width 1.5, with a subtle glow filter (feGaussianBlur stdDeviation=2)
- Below the horizon: very faint horizontal scan-lines — 3 lines at y=65,69,73, stroke #1E3A5F, stroke-width 0.5, opacity 0.4
- "OLA" centered, font-size 46px, font-weight 800, Plus Jakarta Sans
  Fill: left-to-right gradient #F97316 (orange) → #FBBF24 (gold) → #F97316
  glow filter: feGaussianBlur stdDeviation=3 merged with source
- "DIGITAL" at y=74, text-anchor middle, font-size 10px, font-weight 600, letter-spacing 7px, fill #38BDF8, Inter
- ViewBox 0 0 300 80

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c2",
        "label": "Dark hexagon grid bg — OLA electric white, neon underline",
        "prompt": f"""
{BRAND_BRIEF}

Design a dark premium logo:
- Background 300×80, fill #080C18
- Background pattern: draw a subtle hexagonal dot-grid using ~20 small circles (r=0.8) arranged in a hex grid pattern, fill #1E3A5F, opacity 0.5 — creates a tech circuit feel
- "OLA" centered x=150 y=46, font-size 48px, font-weight 800, Plus Jakarta Sans, fill white
  Add a filter: feDiffuseLighting or just feGaussianBlur to create a very subtle white glow (stdDeviation=1.5)
- Under "OLA": a neon underline from x=90 to x=210, y=52, stroke #06B6D4, stroke-width 1.5 with glow filter (stdDeviation=2.5)
- "DIGITAL" at y=68, centered, font-size 10px, font-weight 600, letter-spacing 7px, fill rgba(255,255,255,0.40), Inter
- A small orange square/diamond accent (4×4, rotated 45°) at x=48 y=40 and x=252 y=40 — flanking the OLA text symmetrically
- ViewBox 0 0 300 80

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c3",
        "label": "Dark stacked — OLA vertical gradient cyan-to-blue, strong grid floor",
        "prompt": f"""
{BRAND_BRIEF}

Build on this exact B6 style: dark bg #0A0118, perspective radial lines from vanishing point, horizontal lines getting denser at bottom, OLA with glow, DIGITAL in cyan.

This variant changes:
- Background: #060D1F (dark navy, slightly different from B6)
- The perspective grid: use BOTH radial lines AND horizontal lines but make the radial lines go from a vanishing point at x=150,y=42 outward — more dramatic spread, 9 radial lines spaced evenly. Stroke #3730A3 (deep indigo), opacity 0.35, stroke-width 0.6
- Horizontal lines: 8 lines from y=46 to y=80, getting closer together, stroke #3730A3, opacity decreasing from 0.65 at bottom to 0.05 at top
- "OLA" centered, font-size 46px, font-weight 800, Plus Jakarta Sans
  Fill: TOP-TO-BOTTOM gradient #38BDF8 (bright cyan top) → #0369A1 (deep blue bottom)
  Strong glow filter: feGaussianBlur stdDeviation=4, merged
- Thin line y=52, x=70 to x=230, stroke #F97316, stroke-width 1, glow stdDeviation=2
- "DIGITAL" y=67, centered, 10px, 600, letter-spacing 6px, fill #38BDF8, Inter
- ViewBox 0 0 300 80

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c4",
        "label": "Dark circle emblem — OLA inside glowing circle on dark bg",
        "prompt": f"""
{BRAND_BRIEF}

Design a dark circular emblem logo:
- Background rect 300×80, fill #080C18
- Center: a circle cx=40 cy=40 r=30, fill none, stroke: use gradient from #0EA5E9 to #06B6D4 via a linearGradient on the stroke, stroke-width 2
  Add a subtle outer glow (filter feGaussianBlur stdDeviation=3 on the circle)
- Inside the circle, "OLA" text, cx=40 cy=40, font-size 16px, font-weight 800, Plus Jakarta Sans, fill white, text-anchor middle
- Small wave path inside circle below OLA text: simple 2-hump wave, stroke #F97316, stroke-width 1.5, fill none
- To the right of the circle (starting x=80):
  "OLA" font-size 36px, font-weight 800, Plus Jakarta Sans, fill white, y=38
  "DIGITAL" font-size 11px, font-weight 600, Inter, letter-spacing 5px, fill #38BDF8, y=55
- ViewBox 0 0 300 80

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },

    # ── B7-inspired: geometric marks, icons, monograms ───────────────────────

    {
        "name": "logo-c5",
        "label": "Hexagon mark — OLA inside bold hexagon with wave",
        "prompt": f"""
{BRAND_BRIEF}

Design a geometric hexagon mark logo (inspired by the diamond B7 style but using a hexagon):
- Center a regular hexagon (6 sides, flat-top orientation) at cx=44 cy=44, size r=34
  Stroke #0EA5E9, stroke-width 2.5, fill none, stroke-linejoin round
  Subtle inner glow: duplicate the hexagon path with stroke opacity 0.15, stroke-width 6
- Inside the hexagon: "OLA" font-size 20px, font-weight 800, Plus Jakarta Sans, fill #0EA5E9, text-anchor middle, y=52
- Small single-hump wave path inside hex below "OLA": stroke #F97316, stroke-width 2, fill none
- To the right of hexagon (x starting ~90):
  "OLA Digital" on one line: "OLA" font-size 28px, font-weight 800, fill #0F172A + "Digital" font-size 18px, font-weight 400, fill #64748B
  Baseline y=52
- Below the text line: thin line full width of text, stroke #E2E8F0, stroke-width 1, y=58
- ViewBox 0 0 240 88, white/light background assumed

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c6",
        "label": "Bold O lettermark — oversized O with wave fill, standalone",
        "prompt": f"""
{BRAND_BRIEF}

Design a sophisticated lettermark using a large styled O:
- A large bold letter "O", font-size 80px, font-weight 800, Plus Jakarta Sans, positioned at x=60 y=75, fill none, stroke: linearGradient #0369A1 → #06B6D4 (left to right), stroke-width 3
- Inside the O's open space: clip a wave path to show only inside — use clipPath with an ellipse matching the O's inner space. Draw 2 sinusoidal wave lines (C bezier), stroke #F97316, stroke-width 2, fill none — visible through the O's hollow
- To the right (x=80): "LA" continuing the word, font-size 80px, font-weight 800, Plus Jakarta Sans, fill url(gradient #0369A1→#06B6D4)
- Below full "OLA": "Digital" font-size 18px, font-weight 400, Inter, fill #94A3B8, letter-spacing 1px
- ViewBox 0 0 200 100

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c7",
        "label": "Shield mark — wave inside shield, OLA below",
        "prompt": f"""
{BRAND_BRIEF}

Design a shield/crest shaped logo mark — authoritative and trustworthy:
- A shield path: start M60,8 C20,8 10,30 10,50 C10,72 35,85 60,92 C85,85 110,72 110,50 C110,30 100,8 60,8 Z
  Fill: linearGradient top-to-bottom #0C4A6E → #0EA5E9
  Stroke: none
- Inside the shield, centered at x=60:
  "OLA" font-size 22px, font-weight 800, Plus Jakarta Sans, fill white, y=46, text-anchor middle
  Below: a 2-hump wave path centered at y=56, stroke white, stroke-width 2, fill none, opacity 0.7
  Thin line at y=62, x=26 to x=94, stroke rgba(255,255,255,0.3), stroke-width 0.8
  "OD" very small text y=74, font-size 9px, fill rgba(255,255,255,0.5), letter-spacing 3px, text-anchor middle
- Below the shield (y=100): "OLA DIGITAL" font-size 10px, font-weight 600, Inter, letter-spacing 4px, fill #64748B, text-anchor middle
- ViewBox 0 0 120 112

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-c8",
        "label": "Diamond refined — B7 evolved with gradient fill and glow",
        "prompt": f"""
{BRAND_BRIEF}

This is a refined evolution of logo B7 (diamond monogram). Improve on it significantly:

B7 was: simple diamond outline, OD text inside, OLA DIGITAL below, orange wave. It was too plain.

This version:
- Diamond shape M60,8 L100,48 L60,88 L20,48 Z
  Fill: linearGradient top-to-bottom #0369A1 (top) → #06B6D4 (bottom)
  Stroke: none (filled diamond, not outline)
  Subtle drop shadow filter: feDropShadow dx=0 dy=4 stdDeviation=8 flood-color=#0EA5E9 flood-opacity=0.3
- Inside the diamond:
  Large "O" font-size 38px, font-weight 800, Plus Jakarta Sans, fill white, text-anchor middle, y=44
  Small underline wave inside the O hollow space area: a short wave path, stroke #F97316, stroke-width 2, fill none, centered at y=52
  "D" font-size 14px, font-weight 700, Inter, fill rgba(255,255,255,0.65), letter-spacing 3px, text-anchor middle, y=68
- Below diamond (y=100): "OLA DIGITAL" 10px, 600, Inter, letter-spacing 4px, fill #64748B, text-anchor middle
- Small orange dot circles (r=3, fill #F97316) at the 4 diamond corners (top, bottom, left, right points)
- ViewBox 0 0 120 112

Return ONLY valid SVG starting with <svg and ending with </svg>.
""",
    },
]
LOGO_TASKS_OLD = [
    {
        "name": "logo-b1",
        "label": "Neon glow — dark background, electric blue glow on OLA",
        "prompt": f"""
{BRAND_BRIEF}

Design a bold dark-mode logo SVG:
- Background: rounded rect 320×80 rx=20, fill #0A0F1E (near-black navy)
- "OLA" text: font-size 48px, font-weight 800, Plus Jakarta Sans, fill #38BDF8 (bright cyan)
  Add a subtle glow: use a <filter> with feGaussianBlur + feComposite to create a cyan glow effect behind the text
- "DIGITAL" below OLA: font-size 12px, font-weight 600, Inter, letter-spacing 5px, fill rgba(255,255,255,0.45)
- Left of text: a vertical stack of 3 short horizontal lines (~20px each), spacing 8px, stroke #F97316 (orange), stroke-width 3, stroke-linecap round — like an abstract signal/wifi icon
- ViewBox: 0 0 320 80
- Dark, electric, premium agency vibe

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b2",
        "label": "Circle mark — O as wave circle, stacked layout",
        "prompt": f"""
{BRAND_BRIEF}

Design a logo where the letter O in OLA is replaced by a circular wave mark:
- Create a circle (r=24, cx=24, cy=32) with stroke #0EA5E9, stroke-width 3, fill none
- Inside that circle: a horizontal wave path using C bezier commands, stroke #06B6D4, stroke-width 2, fill none — creating a "water level" effect inside the O circle
- After the circle: "LA" text continuing the word, font-size 44px, font-weight 800, Plus Jakarta Sans, fill #0F172A — positioned to flow naturally after the circle mark
- Below the full "OLA" row: " Digital" in Inter 400, font-size 20px, fill #64748B, left-aligned under the "O" circle
- A thin horizontal rule (line) separating "OLA" from "Digital", stroke #E2E8F0
- ViewBox: 0 0 220 75
- Clever, distinctive, typographic logo where the O IS the brand mark

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b3",
        "label": "Bold all-caps stacked — OLA large, DIGITAL small below, wave slash",
        "prompt": f"""
{BRAND_BRIEF}

Design a strong stacked wordmark SVG:
- "OLA" in massive font: font-size 56px, font-weight 800, Plus Jakarta Sans
  Fill with a left-to-right linear gradient: #0C4A6E (left) to #0EA5E9 (right)
- Directly below, full width: "DIGITAL" font-size 14px, font-weight 600, Inter, letter-spacing 8px, fill #94A3B8, text-anchor start
- Between the two words: a diagonal slash line from bottom-left to top-right of the word gap, stroke #F97316, stroke-width 2.5 — like a separator
- Right edge: a vertical accent bar (3px wide, full height of OLA text), fill #F97316, rx=2
- ViewBox: 0 0 200 80
- Confident, editorial, like a magazine masthead mixed with tech brand

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b4",
        "label": "Rounded pill badge — OLA inside a pill shape",
        "prompt": f"""
{BRAND_BRIEF}

Design a pill/capsule shaped logo badge:
- A wide pill shape: width=260, height=64, rx=32, filled with gradient left-to-right #0369A1 → #06B6D4
- Inside the pill on the left: a small white circle (r=14) with a 2-wave path inside (white, fill none, stroke-width 2) — mini wave mark
- A vertical divider line after the circle: x1=x2, full pill height minus padding, stroke rgba(255,255,255,0.25), stroke-width 1
- "OLA" text after divider: font-size 28px, font-weight 800, Plus Jakarta Sans, fill white
- "DIGITAL" after OLA with a space: font-size 16px, font-weight 400, Inter, fill rgba(255,255,255,0.70)
- All content vertically centered in the pill
- ViewBox: 0 0 260 64
- Friendly, modern, like a SaaS product chip/tag

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b5",
        "label": "Geometric triangle mark — signal/broadcast icon + wordmark",
        "prompt": f"""
{BRAND_BRIEF}

Design a logo with a geometric signal/broadcast mark:
- Left mark: 3 concentric arcs (like a wifi/broadcast symbol rotated 90°, opening to the right)
  Arc 1 (smallest, innermost): r=10, stroke #0EA5E9, stroke-width 3, opacity 1.0
  Arc 2 (medium): r=18, stroke #0EA5E9, stroke-width 2.5, opacity 0.65
  Arc 3 (largest): r=26, stroke #06B6D4, stroke-width 2, opacity 0.35
  All arcs centered at (30, 40), spanning from -60° to +60° (opening rightward)
  A small filled circle at the arc center point: r=4, fill #F97316
- Right of mark (starting at x=62):
  "OLA" font-size 36px, font-weight 800, Plus Jakarta Sans, fill #0F172A, y=44
  "DIGITAL" font-size 11px, font-weight 600, Inter, letter-spacing 4px, fill #94A3B8, y=56
- ViewBox: 0 0 230 72
- Feels like a digital signal / connectivity brand mark

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b6",
        "label": "Retro wave — synthwave aesthetic, gradient sky",
        "prompt": f"""
{BRAND_BRIEF}

Design a logo with a retro-synthwave / vaporwave inspired aesthetic (but still professional and clean):
- Background: 300×80 rect, fill #0A0118 (near-black with purple tint)
- Bottom portion: a retro grid perspective floor using 6-8 horizontal lines getting closer together toward a vanishing point — lines stroke #4F46E5 (indigo), stroke-width 1, opacity decreasing from bottom
- Above the grid: "OLA" in massive text font-size 46px, font-weight 800, Plus Jakarta Sans
  Fill with vertical gradient: top #F97316 (orange) → bottom #EC4899 (pink) — synthwave colors
- "DIGITAL" below in font-size 11px, font-weight 600, letter-spacing 6px, fill #38BDF8 (cyan), Inter
- Thin horizontal glowing line between OLA and DIGITAL: stroke #38BDF8, stroke-width 1, opacity 0.6
- ViewBox: 0 0 300 80
- Unique, memorable, modern-retro — for a bold digital agency

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b7",
        "label": "Monogram OD — initials in geometric diamond",
        "prompt": f"""
{BRAND_BRIEF}

Design a monogram logo using the initials "OD" (OLA Digital):
- A diamond shape (rotated square) 60×60, stroke #0EA5E9, stroke-width 2.5, fill none
- Inside the diamond: "OD" text, font-size 22px, font-weight 800, Plus Jakarta Sans, fill #0EA5E9, text-anchor middle
  "O" slightly larger or bolder than "D" — the O dominates
- Below the diamond: "OLA DIGITAL" in font-size 10px, font-weight 600, Inter, letter-spacing 4px, fill #64748B, text-anchor middle
- A small wave path (single hump) below the "OLA DIGITAL" text: stroke #F97316, stroke-width 2, fill none, centered
- ViewBox: 0 0 120 100, centered composition
- Clean geometric brand mark, works at any size

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
    {
        "name": "logo-b8",
        "label": "Split color — OLA in two tones, inline digital lowercase",
        "prompt": f"""
{BRAND_BRIEF}

Design an elegant split-color wordmark:
- "O" in font-size 52px, font-weight 800, Plus Jakarta Sans, fill #0369A1 (deep ocean blue)
- "L" same size/weight, fill #0EA5E9 (sky blue)
- "A" same size/weight, fill #06B6D4 (bright cyan)
- Each letter is a slightly different shade creating a gradient-through-letters effect
- Immediately after "A" (no space or minimal gap): "digital" in lowercase, font-size 24px, font-weight 400, Inter, fill #94A3B8, baseline-aligned with the caps
- A small orange dot (circle r=4, fill #F97316) placed as a period/accent after "digital"
- Under the full wordmark: a thin full-width line, stroke #E2E8F0, stroke-width 1
- ViewBox: 0 0 280 68
- Sophisticated, typographic, like a premium magazine or design studio

Return ONLY valid SVG code starting with <svg and ending with </svg>.
""",
    },
]


def extract_svg(raw: str) -> str:
    start = raw.find("<svg")
    end   = raw.rfind("</svg>")
    if start == -1 or end == -1:
        raise ValueError("No valid SVG found in response")
    return raw[start:end + 6]


def run():
    for d in [ASSETS, TOOLKIT]:
        d.mkdir(parents=True, exist_ok=True)

    success = 0
    for task in LOGO_TASKS:
        print(f"\n→ Generating '{task['name']}' — {task['label']} ...")
        try:
            raw = call_claude(
                prompt=task["prompt"],
                system_prompt=(
                    "You are a professional SVG logo designer. "
                    "Return ONLY clean, valid SVG code — no markdown, no explanation, no code fences. "
                    "Start directly with <svg and end with </svg>."
                ),
                model="sonnet",
            )
            svg = extract_svg(raw)

            for dest in [ASSETS, TOOLKIT]:
                out = dest / f"{task['name']}.svg"
                out.write_text(svg, encoding="utf-8")
                print(f"  ✓ {out.relative_to(ROOT)}  ({len(svg.encode())//1024} KB)")

            success += 1
        except Exception as e:
            print(f"  ✗ {task['name']}: {e}")

    print(f"\n{success}/{len(LOGO_TASKS)} SVG logos generated.")
    print("Run  python3 tools/generate_brand_toolkit.py  to update the toolkit.")


if __name__ == "__main__":
    run()
