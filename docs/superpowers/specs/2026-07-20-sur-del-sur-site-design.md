# Sur del Sur — Cinematic One-Page Site

## Context

Sur del Sur is a real craft brewery in Sierras Bayas (Olavarría), independent since 2011,
founded by Álvaro, Nacho and Santi. +100 points of sale nationally, medals at the Copa
Argentina de Cervezas, taproom open Fri–Sun from 18h, WhatsApp delivery.

Three brand directions were previously explored in `brand-toolkit/sur-del-sur-mockup.html`:
Pop Playful, Sierras Bayas Rústico (charcoal + copper industrial), Editorial Export
(cream + oxblood serif). This project builds on **Sierras Bayas Rústico**.

Reference inspiration: a tweet showing a "Lumenavo Atelier" site build — full-bleed video
background, large staggered-letter serif headline reveal, minimal navbar with slide-down
entrance, bottom glass-pill bar with rounded logo + two info columns, animated mobile
hamburger menu with fullscreen overlay.

Real photo assets available in `brand-toolkit/assets/sur-del-sur/`:
`tanks_livemusic.jpg` (dark, warm, fermentation tanks — hero background),
`tap_pour.jpg` (tap pour shot — taproom section), `lifestyle_can.jpg`, `real_logo_box.jpg`
(real cursive "Sur del Sur — Compañía Cervecera" logo on packaging, with vintage truck
illustration — reference for wordmark style).

## Goal

Build a standalone, zero-cost, static one-page website for Sur del Sur that recreates the
cinematic mood of the reference (dark, moody, animated typography) using the brewery's real
photos and brand facts, in the Sierras Bayas Rústico palette.

## Non-goals

- No backend, no CMS, no build step, no npm dependencies.
- No video background (static photo instead, per decision below).
- Not a redesign of the existing 3-mockup exploration file — this is a new, separate,
  production-shaped page.

## Tech approach

- Single self-contained file: `sur-del-sur-site/index.html` (HTML + inline `<style>` +
  inline `<script>`, vanilla JS only). Matches the existing pattern used by
  `storm-site/index.html` and `olavarria/*.html` in this repo — no framework, no bundler.
- Fonts via Google Fonts `<link>`: **Bebas Neue** (nav/labels/industrial accents) and
  **Domine** (serif headline + body serif accents) — the same pairing already used in the
  Sierras Bayas Rústico mockup.
- Images referenced via relative path from `brand-toolkit/assets/sur-del-sur/`.

## Palette (from Sierras Bayas Rústico mockup)

```
--char:        #1a1a2e
--char-deep:   #111122
--copper:      #c2661a
--copper-deep: #8a4712
--stone:       #e8e0d0
```

## Page structure

### 1. Hero
- Full-bleed `tanks_livemusic.jpg` background with a dark gradient overlay
  (`--char` → `--char-deep`), object-fit: cover.
- Badge, top-left or centered above headline: "● INDEPENDIENTE DESDE 2011".
- Staggered-letter headline reveal on page load, 3 lines, big serif (Domine):
  - `HECHA`
  - `A MANO,`
  - `SIN APURO` (copper color)
  - Reveal animation: per-letter fade/translateY-in with staggered delay (~30–50ms per
    letter), triggered on load, similar timing/feel to the reference tweet's technique.
- Navbar (fixed, transparent over hero, solid `--char-deep` after scroll):
  - Left: script/serif "Sur del Sur" wordmark (styled after `real_logo_box.jpg` cursive
    logo, rendered in CSS/webfont — no image needed).
  - Center/right links: Cervezas, Taproom, Puntos de Venta.
  - Right: copper pill CTA — "PEDÍ POR WHATSAPP" (links to
    `https://wa.me/<number>` — placeholder number if none on hand, flagged in plan).
  - Entrance animation: slide-down on page load.
- Bottom glass bar (anchored to bottom of hero viewport):
  - Left: small rounded brand mark, scale-in animation.
  - Center: two info columns — "01 — Nuestra Historia" / "02 — El Taproom" (each links to
    its section).
  - Right: glass-effect CTA pill with gradient border-mask, "PEDÍ POR WHATSAPP" (duplicate
    of nav CTA, visible once nav CTA scrolls out of view on mobile).
- Mobile: hamburger icon that animates into an X; opens a fullscreen `--char-deep` overlay
  menu with the same links, staggered divider lines between items on open.

### 2. Historia
- Section on `--stone` (light) background for contrast against the dark hero.
- Copy beats: founded 2011 in Sierras Bayas by Álvaro, Nacho and Santi; started as a hobby
  among friends; grew into one of the country's best breweries; hand-made, own factory,
  no rush.
- Simple layout: kicker label ("01 — Nuestra Historia"), short serif paragraph, small
  timeline/meta row (2011 · Sierras Bayas · Álvaro, Nacho, Santi).
- Scroll-reveal: fade + slide-up via IntersectionObserver as the section enters viewport.

### 3. Cervezas
- `--char` dark background.
- Grid of 3 cards: Rubia, IPA, Stout — each with name, one-line flavor description
  (placeholder copy, flagged for real content in plan), copper accent divider.
- Scroll-reveal same as above, staggered per card.

### 4. Taproom
- `tap_pour.jpg` as a supporting image (not full-bleed — contained, with rounded corners,
  matching the "editorial" restraint of the reference's content columns).
- Copy: taproom open Fri–Sun from 18h, bodegón + beer on tap in Sierras Bayas.
- CTA: WhatsApp delivery link.

### 5. Reconocimiento (stats)
- `--char-deep` background.
- Stat block, large copper numerals (Bebas Neue): `+100` puntos de venta en el país,
  medal at Copa Argentina de Cervezas.
- Numbers can count-up on scroll-into-view (nice-to-have, not required).

### 6. Footer / Contacto
- `--char-deep` background, `--stone` text.
- WhatsApp delivery CTA, address (Sierras Bayas, Olavarría), social links (Instagram
  `@sur.del.sur` if handle confirmed — flagged for confirmation in plan).
- Small print: "Sur del Sur — Compañía Cervecera · Desde 2011".

## Animation summary

- Hero headline: staggered per-letter reveal on load.
- Navbar: slide-down entrance on load.
- Bottom bar: scale-in logo, glass CTA pill.
- Mobile menu: hamburger→X morph, fullscreen overlay, staggered divider-line reveal.
- Scroll sections: IntersectionObserver-driven fade/slide-up reveal, per section
  (and per card within Cervezas grid).
- No video, no external animation libraries — all CSS transitions/keyframes + minimal
  vanilla JS (IntersectionObserver, class toggling).

## Open questions to resolve during planning

- Exact WhatsApp number/delivery link (repo has WhatsApp delivery mentioned but the
  specific number should be confirmed rather than invented).
- Real Instagram handle to confirm before linking in footer.
- Beer lineup copy (Rubia/IPA/Stout descriptions) — placeholder vs. real tasting notes.

## Testing / verification

- Open the file directly in a browser (no server needed, static file) and visually verify:
  hero reveal animation, navbar scroll behavior, mobile menu (via responsive/device
  toolbar), scroll-reveal on all sections, all links resolve or are clearly placeholder.
- Check at both desktop and mobile viewport widths.
