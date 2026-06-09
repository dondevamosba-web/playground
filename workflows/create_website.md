# Workflow: OLA Digital Website

## Objective
Generate and maintain the OLA Digital static website — a complete, production-ready site for the digital marketing agency targeting businesses in Olavarría, Buenos Aires, Argentina.

## Prerequisites
- Python 3.8+
- Write access to the project root

No additional packages needed. The tool uses Python standard library only.

## Inputs
None required at runtime. All brand configuration lives in the `BRAND` dict at the top of `tools/generate_website.py`.

## Execution

**Generate the site:**
```bash
python3 tools/generate_website.py
```

**Preview it:**
```bash
open website/index.html
```

**Output files:**
```
website/index.html              ← the full single-page site
website/assets/logo.svg         ← OLA wordmark SVG
website/assets/favicon.svg      ← wave icon for browser tab
website/assets/css/custom.css   ← animations + Tailwind overrides
```

Re-running the generator always overwrites the output files — the `website/` directory is fully regenerated.

## How to Customize

### Change brand colors / contact info
Edit the `BRAND` dict at the top of `tools/generate_website.py`:
```python
BRAND = {
    "whatsapp_number": "5491162310105",   # +54 9 11 6231-0105
    "email": "hola@oladigital.com.ar",
    "color_primary": "#0EA5E9",           # main blue
    "color_accent": "#F97316",            # orange CTAs
    ...
}
```
Then re-run the generator.

### Update copy (text content)
Each section has its own builder function in the tool:
- `build_hero()` — headline, subheadline, stats
- `build_services()` — uses the `SERVICES` list at the top of the file
- `build_local()` — the "Por qué Olavarría" section and stat cards
- `build_process()` — the 4-step stepper (uses `PROCESS_STEPS` list)
- `build_testimonials()` — uses the `TESTIMONIALS` list (replace with real ones)
- `build_about()` — agency story and values
- `build_contact()` — form and contact info

Edit the relevant list or function, then re-run.

### Add a new service
Add an entry to the `SERVICES` list:
```python
SERVICES = [
    ...
    {
        "title": "Nombre del servicio",
        "description": "Descripción en una o dos oraciones.",
        "icon": '<path stroke-linecap="round" ... />',  # Heroicons path
    },
]
```
Icons: copy any path from https://heroicons.com (outline style, 24px).

## Deployment

The `website/` folder is the deploy root. Any static host works:

| Option | How |
|---|---|
| **Netlify** | Drag-and-drop the `website/` folder at app.netlify.com |
| **Vercel** | `npx vercel website/` or connect the repo and set root to `website/` |
| **GitHub Pages** | Push `website/` contents to a `gh-pages` branch |
| **FTP / cPanel** | Upload all files in `website/` to `public_html/` |

**Custom domain:** Point `oladigital.com.ar` to the host and update the canonical URL and OG tags in `build_head()`.

## Contact Form

The form uses `action="mailto:"` which opens the user's default mail client. This works well on desktop but is unreliable on iOS.

**For a real form backend (recommended):**
1. Sign up at [formspree.io](https://formspree.io) (free tier: 50 submissions/month)
2. Create a form → copy the endpoint URL (e.g. `https://formspree.io/f/xabc1234`)
3. In `build_contact()`, replace:
   ```python
   action="mailto:{brand['email']}"  method="post" enctype="text/plain"
   ```
   with:
   ```python
   action="https://formspree.io/f/xabc1234"  method="POST"
   ```
4. Re-run the generator

## Known Constraints

- **No backend**: The site is 100% static. No server-side logic.
- **Tailwind CDN**: Uses the Play CDN (auto-purge disabled). Fine for production but consider switching to a pinned CDN version URL (`https://cdn.tailwindcss.com/3.4.0`) to avoid surprise API changes.
- **Google Fonts**: Loaded from CDN — requires internet connection in the browser. For offline use, download and self-host the fonts.
- **WhatsApp link format** (Argentina): `https://wa.me/54 9 [area_code_without_0] [number_without_15]`. Olavarría area code: 02284 → use 2284.

## Future Enhancements

- `tools/generate_blog_post.py` — use `claude_call.py` to generate SEO blog posts (e.g., "Cómo aparecer en Google en Olavarría") and inject them as a static `/blog/` section
- `tools/update_testimonials.py` — generate realistic placeholder testimonials via Claude until real ones are collected
- Add Google Analytics / Plausible snippet in `build_head()` once the site is live
- Replace `og-image.png` placeholder with a real 1200×630 screenshot once deployed
