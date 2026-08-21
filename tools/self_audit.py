#!/usr/bin/env python3
"""
Weekly self-audit of the WAT framework: scans cron logs for errors, summarizes
git activity, and flags stale workflows. Output to stdout + .tmp/self_audit.md;
--email drops a Gmail draft.

Usage:
  python3 tools/self_audit.py [--email] [--days 7]
"""
import argparse
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))

ERR_RE = re.compile(r"error|traceback|failed|exception", re.I)


def log_errors(days):
    cutoff = datetime.now() - timedelta(days=days)
    lines = []
    logs = list(ROOT.glob(".tmp/*.log"))
    for log in logs:
        if not log.exists() or datetime.fromtimestamp(log.stat().st_mtime) < cutoff:
            continue
        errs = [l for l in log.read_text(errors="ignore").splitlines()[-400:] if ERR_RE.search(l)]
        if errs:
            lines.append(f"- **{log.name}**: {len(errs)} líneas con error. Última: `{errs[-1][:110]}`")
    return lines or ["- Sin errores en logs de cron 👌"]


def git_activity(days):
    out = subprocess.run(
        ["git", "log", f"--since={days} days ago", "--format=%as %s"],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    commits = out.splitlines()
    return [f"- {len(commits)} commits en {days} días"] + [f"  - {c}" for c in commits[:10]]


def cron_inventory():
    out = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    jobs = [l for l in out.splitlines() if l.strip() and not l.startswith("#")]
    return [f"- {len(jobs)} cron jobs activos"] + [f"  - `{j}`" for j in jobs]


def launchd_health():
    """Flag playground launchd jobs that aren't loaded, exited nonzero, or
    whose log went silent past the job's max_silence_hours (= not firing)."""
    from generate_launchd_plists import JOBS, PREFIX, KEEP_ALIVE
    out = subprocess.run(["launchctl", "list"], capture_output=True, text=True).stdout
    status = {}  # label -> last exit status
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2].startswith(PREFIX):
            status[parts[2]] = parts[1]

    problems = []
    now = datetime.now()
    for name, (_, _, log, max_h) in JOBS.items():
        label = PREFIX + name
        if label not in status:
            problems.append(f"- ⚠️ **{name}**: NO está cargado en launchd")
            continue
        if status[label] not in ("0", "-"):
            problems.append(f"- ⚠️ **{name}**: último exit status {status[label]}")
        if name in KEEP_ALIVE:
            continue  # daemons: loaded check is enough, no per-run log line
        path = Path(log) if log.startswith("/") else ROOT / log
        if not path.exists():
            problems.append(f"- ⚠️ **{name}**: log `{log}` no existe (nunca corrió)")
        elif now - datetime.fromtimestamp(path.stat().st_mtime) > timedelta(hours=max_h):
            age_d = (now - datetime.fromtimestamp(path.stat().st_mtime)).days
            problems.append(f"- ⚠️ **{name}**: log sin actividad hace {age_d} días (esperado cada ≤{max_h}h)")
    header = f"- {len(status)}/{len(JOBS)} jobs launchd cargados"
    return [header] + (problems or ["- Todos los jobs corrieron dentro de su ventana esperada 👌"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--email", action="store_true")
    a = ap.parse_args()

    parts = [f"# Self-audit — {date.today()}", "", "## Errores en logs"]
    parts += log_errors(a.days)
    parts += ["", "## Actividad git"]
    parts += git_activity(a.days)
    parts += ["", "## Jobs launchd (playground)"]
    parts += launchd_health()
    parts += ["", "## Cron jobs (restantes)"]
    parts += cron_inventory()
    parts += ["", "## Acción sugerida",
              "- Revisar errores de arriba; si un tool falla recurrente, arreglarlo y actualizar su workflow (loop de auto-mejora del CLAUDE.md)."]
    body = "\n".join(parts)
    print(body)
    (ROOT / ".tmp" / "self_audit.md").write_text(body)

    if a.email:
        from gmail_draft import create_draft
        create_draft(to="carminattiguido@gmail.com",
                     subject=f"Self-audit semana {date.today():%d/%m}", body=body)
        print("\n(Draft creado en Gmail)")


if __name__ == "__main__":
    main()
