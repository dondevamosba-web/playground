#!/usr/bin/env python3
"""Generate + load launchd LaunchAgents for playground scheduled jobs.

Replaces cron because launchd fires missed StartCalendarInterval jobs on wake
(cron silently skips them while the Mac sleeps). JOBS below is the single
source of truth; self_audit.py imports it to check log freshness.

Each job appends a "[launchd] <name> exit=N <timestamp>" line to its log on
every run, so a log that goes silent past its max_silence_hours means the job
is not firing at all.

Usage:
  python3 tools/generate_launchd_plists.py            # write plists + (re)load
  python3 tools/generate_launchd_plists.py --dry-run  # write plists only
"""
import os
import plistlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENTS = Path.home() / "Library" / "LaunchAgents"
PY = ".venv/bin/python3"
PREFIX = "com.playground."
WEEKDAYS = [1, 2, 3, 4, 5]  # launchd: 0/7=Sun, 1=Mon
RUN_AT_LOAD = {"catchup-missed"}  # jobs that also fire at boot/login
KEEP_ALIVE = {"approval-server"}  # daemons: always running, no calendar


def cal(hour, minute, weekdays=None, day=None):
    base = {"Hour": hour, "Minute": minute}
    if day is not None:
        return [{**base, "Day": day}]
    if weekdays is not None:
        return [{**base, "Weekday": w} for w in weekdays]
    return [base]


def inbound_chain():
    steps = ["import_netlify_leads", "score_inbound_leads", "draft_inbound_leads"]
    return " && ".join(f"{PY} tools/{s}.py" for s in steps)


# -exec rm instead of -delete: BSD find refuses -delete under launchd
# ("forbidden when the current directory cannot be opened")
CLEANUP = (
    r"find .tmp -type f \( -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' "
    r"-o -name '*.mp4' -o -name '*.mov' -o -name '*.gif' -o -name '*.webp' \) "
    "-mtime +30 -exec rm -f {} + && "
    "find .tmp -mindepth 1 -type d -empty -exec rmdir {} + 2>/dev/null; true"
)

# name: (command run from ROOT, calendar entries, log path, max_silence_hours)
# max_silence_hours = longest normal gap between runs + buffer; self_audit
# flags the job if its log mtime is older than that.
JOBS = {
    "send-drafts": (
        f"{PY} tools/send_priority_drafts.py --limit 15",
        cal(13, 0, WEEKDAYS) + cal(14, 30, WEEKDAYS) + cal(16, 0, WEEKDAYS)
        + cal(17, 30, WEEKDAYS) + cal(19, 0, WEEKDAYS) + cal(20, 30, WEEKDAYS),
        ".tmp/send_log.txt", 80),
    "send-drafts-late": (
        f"{PY} tools/send_priority_drafts.py --limit 10",
        cal(22, 0, WEEKDAYS), ".tmp/send_log.txt", 80),
    "fiestas-queue": (
        f"{PY} tools/queue_event_posts.py",
        cal(9, 0), ".tmp/cron_fiestas_queue.log", 26),
    "fiestas-autoqueue": (
        f"{PY} tools/auto_fiestas_queue.py",
        cal(8, 0), ".tmp/cron_fiestas_autoqueue.log", 26),
    "inbound-leads": (
        inbound_chain(), cal(10, 0), ".tmp/cron_inbound.log", 26),
    "token-health": (
        f"{PY} tools/check_token_health.py",
        cal(9, 0, [1]), ".tmp/cron_token_health.log", 8 * 24),
    "gastos-close": (
        f"{PY} tools/gastos_monthly_close.py",
        cal(9, 5, day=1), ".tmp/cron_gastos.log", 17 * 24),
    "gastos-burn": (
        f"{PY} tools/gastos_monthly_close.py --burn-check",
        cal(9, 5, day=15), ".tmp/cron_gastos.log", 17 * 24),
    "backup": (
        f"{PY} tools/backup_playground.py",
        # log in .tmp, not /tmp: macOS wipes /tmp and self_audit would false-alarm
        cal(9, 0, [1]), ".tmp/cron_backup.log", 8 * 24),
    "morning-briefing": (
        f"{PY} tools/morning_briefing.py --email",
        cal(8, 30, WEEKDAYS), ".tmp/cron_briefing.log", 80),
    "competitor-watcher": (
        f"{PY} tools/competitor_watcher.py",
        cal(9, 30, [1]), ".tmp/cron_competitor.log", 8 * 24),
    "self-audit": (
        f"{PY} tools/self_audit.py --email",
        cal(19, 0, [0]), ".tmp/cron_audit.log", 8 * 24),
    "inbox-monitor": (
        f"{PY} tools/ig_inbox_monitor.py",
        cal(9, 0) + cal(13, 0) + cal(17, 0) + cal(21, 0),
        ".tmp/cron_inbox_monitor.log", 26),
    # cloud routine "Instagram Publisher (playground)" is DISABLED: the cloud
    # sandbox can't reach graph.facebook.com (egress blocked). Publishing is
    # local until that env allows Instagram API traffic.
    # 3x/day — queues back up at 1/day (Storm 47, Empleo 61 due on 2026-07-06);
    # staggered off publish-approved's :05 slots
    "publish-one-each": (
        f"{PY} tools/publish_one_each.py",
        cal(11, 0) + cal(15, 0) + cal(18, 0), ".tmp/cron_publish.log", 26),
    "publish-approved": (
        f"{PY} tools/publish_all_approved.py",
        cal(13, 5) + cal(15, 5) + cal(17, 5) + cal(19, 5) + cal(21, 5),
        ".tmp/cron_publish_approved.log", 26),
    "tmp-cleanup": (
        CLEANUP, cal(10, 0, [1]), ".tmp/cron_cleanup.log", 8 * 24),
    # fresh queue preview + FEBA review page every morning — Guido reviews daily
    "preview": (
        f"{PY} tools/preview_next_posts.py --per-account 10"
        f" && {PY} tools/fiestas_review_page.py",
        cal(8, 15), ".tmp/cron_preview.log", 26),
    # reschedule/expire posts missed while the Mac was off; also fires at boot
    "catchup-missed": (
        f"{PY} tools/catchup_missed_posts.py",
        cal(8, 10), ".tmp/cron_catchup.log", 26),
    # weekly engagement ranking (likes+comments via IG API) → HTML + Gmail draft
    "engagement-report": (
        f"{PY} tools/engagement_report.py --email",
        cal(9, 45, [1]), ".tmp/cron_engagement.log", 8 * 24),
    # daily "HOY" story for Fiestas with tonight's events (silent if none)
    "fiestas-today-story": (
        f"{PY} tools/fiestas_today_story.py",
        cal(11, 0), ".tmp/cron_today_story.log", 26),
    # "ESTE FINDE" story 3x/week (Thu 18h anticipo, Fri+Sat 12h) — Guido 2026-07-10
    "fiestas-finde-story": (
        f"{PY} tools/fiestas_weekend_story.py --publish",
        cal(18, 0, [4]) + cal(12, 0, [5]) + cal(12, 0, [6]),
        ".tmp/cron_finde_story.log", 4 * 24),
    # queue depth check 2x/week (Mon+Thu); auto-refills accounts under 25
    # future posts — with 3 publishes/day a weekly check left gaps
    "queue-health": (
        f"{PY} tools/queue_health.py",
        cal(9, 0, [1, 4]), ".tmp/cron_queue_health.log", 5 * 24),
    # validated image candidates for Techno rows without media (col L)
    "techno-candidates": (
        f"{PY} tools/techno_image_candidates.py",
        cal(9, 10, [3]), ".tmp/cron_techno_cand.log", 8 * 24),
    # localhost server backing the approve/skip buttons in the preview HTML
    "approval-server": (
        f"{PY} tools/approval_server.py",
        None, ".tmp/approval_server.log", 26),
}


def write_plist(name, cmd, entries, log):
    label = PREFIX + name
    wrapped = (
        f"cd {ROOT} && {{ {cmd} ; }} >> {log} 2>&1; "
        f'echo "[launchd] {name} exit=$? $(date \'+%F %T\')" >> {log}'
    )
    plist = {
        "Label": label,
        "ProgramArguments": ["/bin/zsh", "-c", wrapped],
    }
    if name in KEEP_ALIVE:
        plist["KeepAlive"] = True
        plist["RunAtLoad"] = True
    else:
        plist["StartCalendarInterval"] = entries
        if name in RUN_AT_LOAD:
            plist["RunAtLoad"] = True  # also fire when the Mac boots / user logs in
    path = AGENTS / f"{label}.plist"
    with open(path, "wb") as f:
        plistlib.dump(plist, f)
    return path


def load(path, label):
    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"],
                   capture_output=True)
    r = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:  # older launchctl fallback
        subprocess.run(["launchctl", "unload", str(path)], capture_output=True)
        r = subprocess.run(["launchctl", "load", str(path)],
                           capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def main():
    dry = "--dry-run" in sys.argv
    AGENTS.mkdir(parents=True, exist_ok=True)
    failures = 0
    for name, (cmd, entries, log, _) in JOBS.items():
        path = write_plist(name, cmd, entries, log)
        if dry:
            print(f"wrote {path.name}")
            continue
        ok, msg = load(path, PREFIX + name)
        print(f"{'loaded' if ok else 'FAILED'} {PREFIX + name}" + ("" if ok else f": {msg}"))
        failures += 0 if ok else 1
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
