#!/usr/bin/env python3
"""Build dashboard.html: overview of workflows, tools, backlog, and recent git activity."""
import ast
import html
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git_last_dates():
    """Map repo-relative path -> last commit date (one git call for the whole repo)."""
    out = subprocess.run(
        ["git", "log", "--format=%x01%as", "--name-only"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout
    dates, current = {}, None
    for line in out.splitlines():
        if line.startswith("\x01"):
            current = line[1:]
        elif line.strip() and current:
            dates.setdefault(line.strip(), current)
    return dates


def first_heading(md_path):
    for line in md_path.read_text(errors="ignore").splitlines():
        if line.startswith("#"):
            return line.lstrip("# ").strip()
    return ""


def tool_summary(py_path):
    try:
        doc = ast.get_docstring(ast.parse(py_path.read_text(errors="ignore")))
        if doc:
            return doc.strip().splitlines()[0]
    except SyntaxError:
        pass
    return ""


def collect():
    dates = git_last_dates()
    workflows = []
    for p in sorted((ROOT / "workflows").rglob("*.md")):
        rel = p.relative_to(ROOT)
        group = rel.parts[1] if len(rel.parts) > 2 else "general"
        workflows.append((group, p.stem, first_heading(p), dates.get(str(rel), "—")))
    tools = []
    for p in sorted((ROOT / "tools").glob("*.py")):
        rel = str(p.relative_to(ROOT))
        tools.append((p.name, tool_summary(p), dates.get(rel, "—")))
    backlog = []
    bl = ROOT / "BACKLOG.md"
    if bl.exists():
        for line in bl.read_text().splitlines():
            m = re.match(r"- ([☐◐✓]) (#\d+ .+?) — ", line)
            if m:
                backlog.append((m.group(1), m.group(2)))
    return workflows, tools, backlog


def render(workflows, tools, backlog):
    e = html.escape
    done = sum(1 for s, _ in backlog if s == "✓")
    wip = sum(1 for s, _ in backlog if s == "◐")
    rows_w = "\n".join(
        f"<tr><td class='grp'>{e(g)}</td><td>{e(n)}</td><td>{e(t)}</td><td class='dt'>{e(d)}</td></tr>"
        for g, n, t, d in workflows)
    rows_t = "\n".join(
        f"<tr><td>{e(n)}</td><td>{e(s)}</td><td class='dt'>{e(d)}</td></tr>"
        for n, s, d in tools)
    items_b = "\n".join(
        f"<li class='s{ {'☐':'todo','◐':'wip','✓':'done'}[s] }'>{s} {e(t)}</li>"
        for s, t in backlog)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WAT Dashboard</title><style>
body{{font:14px/1.5 -apple-system,sans-serif;background:#0f0f14;color:#e8e8ee;max-width:1000px;margin:0 auto;padding:24px}}
h1{{font-size:20px}} h2{{font-size:16px;margin-top:32px;border-bottom:1px solid #2a2a35;padding-bottom:6px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td{{padding:4px 8px;border-bottom:1px solid #1d1d26;vertical-align:top}}
.grp{{color:#9f7aea;white-space:nowrap}} .dt{{color:#666;white-space:nowrap}}
ul{{list-style:none;padding:0}} li{{padding:3px 0}}
.stodo{{color:#aaa}} .swip{{color:#f6e05e}} .sdone{{color:#68d391}}
.meta{{color:#666;font-size:12px}}
</style></head><body>
<h1>WAT Dashboard</h1>
<p class="meta">Generado {datetime.now():%Y-%m-%d %H:%M} · {len(workflows)} workflows · {len(tools)} tools · backlog {done}✓ {wip}◐ {len(backlog) - done - wip}☐</p>
<h2>Backlog ({len(backlog)})</h2><ul>{items_b}</ul>
<h2>Workflows ({len(workflows)})</h2><table>{rows_w}</table>
<h2>Tools ({len(tools)})</h2><table>{rows_t}</table>
</body></html>"""


if __name__ == "__main__":
    w, t, b = collect()
    out = ROOT / "dashboard.html"
    out.write_text(render(w, t, b))
    print(f"Wrote {out} ({len(w)} workflows, {len(t)} tools, {len(b)} backlog items)")
