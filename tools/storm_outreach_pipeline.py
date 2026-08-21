#!/usr/bin/env python3
"""
One-command Storm cold outreach pipeline: scrape → ads check → emails → score → drafts → log.

Usage:
  python3 tools/storm_outreach_pipeline.py --vertical roofing --cities "Austin TX,Denver CO" --limit 30
  python3 tools/storm_outreach_pipeline.py --vertical hvac --skip-scrape   # reuse existing leads JSON
  python3 tools/storm_outreach_pipeline.py --vertical plumbing --dry-run   # stop before Gmail drafts

Verticals with dedicated scrapers: roofing, hvac, plumbing, windows.
Each step is the existing standalone tool; this just chains them and stops on failure.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PY = sys.executable

SCRAPERS = {
    "roofing": "scrape_roofing_gmaps.py",
    "hvac": "scrape_hvac_gmaps.py",
    "plumbing": "scrape_plumbing_gmaps.py",
    "windows": "scrape_windows_gmaps.py",
}
LOGGERS = {
    "roofing": "log_roofing_outreach.py",
    "hvac": "log_hvac_outreach.py",
    "plumbing": "log_plumbing_outreach.py",
}


def run(step, cmd):
    print(f"\n=== {step}: {' '.join(cmd[1:])}")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"Pipeline stopped at '{step}' (exit {r.returncode}). Fix and rerun with --skip-scrape to reuse leads.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=sorted(SCRAPERS))
    ap.add_argument("--cities", help="Comma-separated cities (default: scraper's list)")
    ap.add_argument("--limit", type=int, default=30, help="Max leads per city")
    ap.add_argument("--min-tier", default="B")
    ap.add_argument("--skip-scrape", action="store_true", help="Reuse existing .tmp/<vertical>_leads.json")
    ap.add_argument("--dry-run", action="store_true", help="Stop after scoring; no Gmail drafts")
    a = ap.parse_args()

    leads = ROOT / ".tmp" / f"{a.vertical}_leads.json"
    t = lambda name: str(ROOT / "tools" / name)

    if not a.skip_scrape:
        cmd = [PY, t(SCRAPERS[a.vertical]), "--limit", str(a.limit)]
        if a.cities:
            cmd += ["--cities", a.cities]
        run("scrape", cmd)
    elif not leads.exists():
        sys.exit(f"--skip-scrape but {leads} doesn't exist")

    run("fb-ads-check", [PY, t("check_fb_ads.py"), "--input", str(leads)])
    run("emails", [PY, t("scrape_emails.py"), "--input", str(leads)])
    run("score", [PY, t("score_leads.py"), "--niche", a.vertical])

    if a.dry_run:
        print("\nDry run: leads scored, no drafts created.")
        return

    drafts = ROOT / "tools" / f"generate_{a.vertical}_drafts.py"
    if drafts.exists():
        run("drafts", [PY, str(drafts), "--min-tier", a.min_tier])
    else:
        run("drafts", [PY, t("generate_outreach_drafts.py"), "--vertical", a.vertical])

    if a.vertical in LOGGERS:
        run("log", [PY, t(LOGGERS[a.vertical])])
    print("\nPipeline complete. Review drafts in Gmail before sending.")


if __name__ == "__main__":
    main()
