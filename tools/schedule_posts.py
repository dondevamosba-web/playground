"""
Content posting scheduler for Ola Digital.

Generates a weekly posting schedule based on best-time-to-post benchmarks
and lists which videos/content to post on each day.

Also creates a Gmail draft with the weekly plan so you have it in your inbox.

Usage:
  python3 tools/schedule_posts.py --plan              # print this week's schedule
  python3 tools/schedule_posts.py --plan --draft      # plan + Gmail draft
  python3 tools/schedule_posts.py --content video1.mp4 video2.mp4 video3.mp4
"""

import argparse
import os
import sys
from datetime import date, timedelta, datetime

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

# Best posting times (EST) based on Meta / Instagram benchmarks for service businesses
# Format: {weekday_name: [(hour, minute, label), ...]}
BEST_TIMES = {
    "Monday":    [(9, 0,  "morning"), (18, 0, "evening")],
    "Tuesday":   [(8, 0,  "morning"), (17, 0, "evening")],
    "Wednesday": [(11, 0, "midday"),  (19, 0, "evening")],
    "Thursday":  [(9, 0,  "morning"), (18, 0, "evening")],
    "Friday":    [(10, 0, "morning")],
    "Saturday":  [(10, 0, "morning")],
    "Sunday":    [],   # low engagement for B2B/local services
}

# Content type rotation for a healthy feed
CONTENT_ROTATION = [
    "Educational reel (tip / how-to)",
    "Social proof (results / testimonial)",
    "Behind the scenes / process",
    "Educational reel (myth / mistake)",
    "Call to action / offer reel",
    "Engagement post (question / poll)",
    "Repurposed long-form clip",
]


def next_monday(ref: date = None) -> date:
    today = ref or date.today()
    days_ahead = 0 - today.weekday()   # Monday is 0
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def build_schedule(start: date, content_files: list = None) -> list[dict]:
    slots = []
    content_idx = 0
    for offset in range(7):
        day = start + timedelta(days=offset)
        day_name = day.strftime("%A")
        times = BEST_TIMES.get(day_name, [])
        for hour, minute, label in times:
            post_dt = datetime(day.year, day.month, day.day, hour, minute)
            content_type = CONTENT_ROTATION[content_idx % len(CONTENT_ROTATION)]
            content_file = content_files[content_idx] if content_files and content_idx < len(content_files) else None
            slots.append({
                "date":         day.isoformat(),
                "day":          day_name,
                "time":         f"{hour:02d}:{minute:02d} EST",
                "label":        label,
                "content_type": content_type,
                "file":         content_file,
                "post_cmd":     _build_post_cmd(post_dt, content_file),
            })
            content_idx += 1
    return slots


def _build_post_cmd(dt: datetime, file: str = None) -> str:
    iso = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")   # assume EST == UTC-0 for scheduling
    if file:
        return (f"python3 tools/post_instagram.py --type reel "
                f"--video-url <UPLOAD_URL> --caption \"$(cat caption.txt)\" "
                f"--schedule {iso}")
    return f"# schedule {iso}"


def print_schedule(slots: list):
    print(f"\n── Weekly Posting Schedule ─────────────────────────────\n")
    current_day = ""
    for s in slots:
        if s["day"] != current_day:
            current_day = s["day"]
            print(f"  {s['day']} {s['date']}")
        file_label = f"  [{s['file']}]" if s["file"] else ""
        print(f"    {s['time']}  {s['content_type']}{file_label}")
    print(f"\n  Total posts scheduled: {len(slots)}")


def build_draft_body(slots: list, week_start: date) -> str:
    lines = [
        f"Weekly Content Plan — {week_start.strftime('%B %d')} to "
        f"{(week_start + timedelta(days=6)).strftime('%B %d, %Y')}",
        "",
        f"Total posts: {len(slots)}",
        "",
    ]
    current_day = ""
    for s in slots:
        if s["day"] != current_day:
            current_day = s["day"]
            lines.append(f"{s['day']} {s['date']}")
        file_label = f" [{s['file']}]" if s["file"] else ""
        lines.append(f"  {s['time']} — {s['content_type']}{file_label}")
    lines += ["", "Upload videos and captions via post_instagram.py", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan",    action="store_true", help="Print this week's schedule")
    parser.add_argument("--draft",   action="store_true", help="Also create Gmail draft")
    parser.add_argument("--content", nargs="*", default=None,
                        help="Video files to assign to slots")
    parser.add_argument("--week",    default=None,
                        help="Week start date YYYY-MM-DD (default: next Monday)")
    args = parser.parse_args()

    start = date.fromisoformat(args.week) if args.week else next_monday()
    slots = build_schedule(start, content_files=args.content)

    print_schedule(slots)

    # Save schedule JSON
    import json
    os.makedirs(os.path.join(ROOT, ".tmp"), exist_ok=True)
    out = os.path.join(ROOT, ".tmp", f"schedule_{start.isoformat()}.json")
    with open(out, "w") as f:
        json.dump(slots, f, indent=2)
    print(f"\n  Saved → {out}")

    if args.draft:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        from gmail_draft import create_draft
        subject = f"Ola Digital — Content Schedule {start.strftime('%B %d')}–{(start + timedelta(days=6)).strftime('%d, %Y')}"
        body = build_draft_body(slots, start)
        result = create_draft(to="carminattiguido@gmail.com", subject=subject, body=body)
        print(f"\n  Gmail draft → ID: {result.get('draft_id')}")


if __name__ == "__main__":
    main()
