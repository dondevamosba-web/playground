#!/usr/bin/env python3
"""
Generate an HTML preview of .tmp/tech_posts.json for approval.
Opens in the default browser automatically.

Usage:
  python tools/preview_tech_posts.py
  python tools/preview_tech_posts.py --input .tmp/tech_posts.json
  python tools/preview_tech_posts.py --no-open   # generate HTML without opening browser
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_INPUT = ROOT / ".tmp" / "tech_posts.json"
OUTPUT_HTML = ROOT / ".tmp" / "tech_posts_preview.html"

BRAND_COLORS = {
    "apple": {"bg": "#1d1d1f", "text": "#f5f5f7", "accent": "#0071e3"},
    "samsung": {"bg": "#1428a0", "text": "#ffffff", "accent": "#12d3ff"},
    "playstation": {"bg": "#003087", "text": "#ffffff", "accent": "#00aeef"},
}

TYPE_BADGES = {
    "offer": ("Oferta", "#d4edda", "#155724"),
    "feature": ("Feature", "#cce5ff", "#004085"),
    "launch": ("Lanzamiento", "#fff3cd", "#856404"),
    "meme": ("Meme", "#f8d7da", "#721c24"),
}


def render_card(post: dict) -> str:
    brand = post.get("brand", "apple")
    colors = BRAND_COLORS.get(brand, BRAND_COLORS["apple"])
    post_type = post.get("type", "offer")
    badge_label, badge_bg, badge_color = TYPE_BADGES.get(post_type, ("Post", "#eee", "#333"))
    post_id = post.get("id", "?")

    caption = post.get("caption", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    hashtags = " ".join(post.get("hashtags", []))
    product = post.get("product", "")
    price = post.get("price", "")

    image_url = post.get("image_url")
    if image_url:
        image_html = f'<img src="{image_url}" style="width:100%;height:220px;object-fit:cover;">'
    else:
        image_html = f'''
        <div style="width:100%;height:220px;background:{colors['bg']};display:flex;flex-direction:column;
                    align-items:center;justify-content:center;color:{colors['text']};gap:8px;">
          <div style="font-size:28px;font-weight:700;">{brand.upper()}</div>
          {f'<div style="font-size:13px;opacity:0.7;">{product}</div>' if product else ''}
          {f'<div style="font-size:22px;font-weight:600;color:{colors["accent"]};">${price}</div>' if price else ''}
          <div style="font-size:11px;opacity:0.5;margin-top:4px;">Agregar imagen → image_url en JSON</div>
        </div>'''

    return f'''
    <div class="card" id="card-{post_id}">
      <div class="card-header">
        <div class="avatar"></div>
        <span class="username">@techno.apple.ok</span>
        <span class="type-badge" style="background:{badge_bg};color:{badge_color};">{badge_label}</span>
      </div>
      {image_html}
      <div class="card-body">
        <div class="caption">{caption}</div>
        <div class="hashtags">{hashtags}</div>
      </div>
      <div class="card-footer">
        <input type="checkbox" class="approve-check" data-id="{post_id}" id="chk-{post_id}">
        <label for="chk-{post_id}" class="approve-label">Aprobar post #{post_id}</label>
      </div>
    </div>'''


def build_html(posts: list) -> str:
    cards = "\n".join(render_card(p) for p in posts)
    posts_json = json.dumps(posts, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Techno Preview — Aprobar Posts</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #fafafa; }}

    .sticky-bar {{
      position: sticky; top: 0; background: white; border-bottom: 1px solid #ddd;
      padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;
      z-index: 100; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .sticky-bar h1 {{ font-size: 16px; font-weight: 600; color: #111; }}
    .sticky-bar .meta {{ font-size: 13px; color: #888; }}
    .btn {{ background: #0095f6; color: white; border: none; border-radius: 8px; padding: 8px 18px;
             cursor: pointer; font-size: 14px; font-weight: 600; transition: background 0.2s; }}
    .btn:hover {{ background: #0081d6; }}
    .btn-outline {{ background: white; color: #0095f6; border: 1px solid #0095f6; margin-left: 8px; }}
    .btn-outline:hover {{ background: #f0f7ff; }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; padding: 24px; max-width: 1400px; margin: 0 auto; }}

    .card {{ background: white; border-radius: 12px; box-shadow: 0 1px 8px rgba(0,0,0,0.08); overflow: hidden; transition: box-shadow 0.2s; }}
    .card.selected {{ box-shadow: 0 0 0 2px #0095f6, 0 4px 16px rgba(0,149,246,0.15); }}
    .card-header {{ display: flex; align-items: center; padding: 12px 14px; border-bottom: 1px solid #efefef; }}
    .avatar {{ width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); flex-shrink: 0; }}
    .username {{ margin-left: 10px; font-weight: 600; font-size: 14px; color: #262626; }}
    .type-badge {{ margin-left: auto; font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 600; white-space: nowrap; }}
    .card-body {{ padding: 14px; }}
    .caption {{ white-space: pre-wrap; font-size: 14px; line-height: 1.55; color: #262626; }}
    .hashtags {{ color: #00376b; font-size: 13px; margin-top: 8px; line-height: 1.5; }}
    .card-footer {{ padding: 10px 14px; border-top: 1px solid #efefef; display: flex; align-items: center; gap: 10px; }}
    .approve-check {{ width: 18px; height: 18px; cursor: pointer; accent-color: #0095f6; }}
    .approve-label {{ font-size: 13px; color: #555; cursor: pointer; }}

    .commands-section {{ margin: 0 24px 24px; }}
    .commands-box {{ background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 10px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 13px; white-space: pre-wrap; line-height: 1.6; display: none; }}
    .commands-box.visible {{ display: block; }}
    .copy-feedback {{ display: none; color: #28a745; font-size: 13px; margin-left: 10px; font-weight: 600; }}
    .empty-state {{ padding: 60px 24px; text-align: center; color: #aaa; font-size: 15px; }}
  </style>
</head>
<body>

<div class="sticky-bar">
  <div>
    <h1>@techno.apple.ok — Preview</h1>
    <div class="meta" id="summary">Cargando...</div>
  </div>
  <div>
    <button class="btn" onclick="selectAll()">Aprobar todos</button>
    <button class="btn btn-outline" onclick="generateCommands()">Generar comandos</button>
  </div>
</div>

<div class="grid" id="grid">
  {cards if posts else '<div class="empty-state">No hay posts en .tmp/tech_posts.json</div>'}
</div>

<div class="commands-section">
  <div id="commands-box" class="commands-box"></div>
  <div style="margin-top:10px;display:flex;align-items:center;">
    <span id="copy-feedback" class="copy-feedback">Copiado!</span>
  </div>
</div>

<script>
const posts = {posts_json};

function updateSummary() {{
  const checked = document.querySelectorAll(".approve-check:checked").length;
  document.getElementById("summary").textContent = `${{checked}} de ${{posts.length}} posts aprobados`;
}}

function selectAll() {{
  document.querySelectorAll(".approve-check").forEach(c => c.checked = true);
  document.querySelectorAll(".card").forEach(c => c.classList.add("selected"));
  updateSummary();
}}

function generateCommands() {{
  const approved = [];
  document.querySelectorAll(".approve-check:checked").forEach(c => {{
    approved.push(parseInt(c.dataset.id));
  }});

  if (!approved.length) {{
    alert("No hay posts aprobados. Chequeá al menos uno.");
    return;
  }}

  const approvedPosts = posts.filter(p => approved.includes(p.id));
  const lines = approvedPosts.map(p => {{
    const caption = p.caption.replace(/"/g, '\\\\"');
    const imageArg = p.image_url ? `--image-url "${{p.image_url}}"` : `--image-url "URL_DE_IMAGEN_AQUI"`;
    return `# Post #${{p.id}} — ${{p.brand}} / ${{p.type}}\\npython tools/post_instagram.py --account techno --type single ${{imageArg}} --caption "${{caption}}"`;
  }});

  const box = document.getElementById("commands-box");
  box.textContent = lines.join("\\n\\n");
  box.classList.add("visible");
  box.scrollIntoView({{ behavior: "smooth", block: "start" }});
}}

document.querySelectorAll(".approve-check").forEach(c => {{
  c.addEventListener("change", function() {{
    const card = document.getElementById("card-" + this.dataset.id);
    card.classList.toggle("selected", this.checked);
    updateSummary();
  }});
}});

updateSummary();
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Preview tech posts before approving")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found. Run generate_tech_posts.py first.")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        posts = json.load(f)

    html = build_html(posts)
    OUTPUT_HTML.parent.mkdir(exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Preview generado → {OUTPUT_HTML}")
    print(f"Posts: {len(posts)} total")

    if not args.no_open:
        if sys.platform == "darwin":
            subprocess.run(["open", str(OUTPUT_HTML)])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", str(OUTPUT_HTML)])
        else:
            import webbrowser
            webbrowser.open(str(OUTPUT_HTML))


if __name__ == "__main__":
    main()
