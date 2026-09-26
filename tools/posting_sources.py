"""
Where each Instagram account's posts live, shared by apply_artifact_decisions.py
and cache_thumbnails.py (and mirrored in the Mesa de Posteos artifact).

- The unified approval sheet: one tab per account, rows queued for approval.
- Content calendars: one sheet per auto-posting account, one dated row per post.
Column numbers are 0-based.
"""
import os

APPROVAL_SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
APPROVAL_TABS = ["Ola Digital", "Storm", "Fiestas", "Techno"]
# Queued At | Caption | Image URL | Schedule Date | Status | Comments | Post ID | Video URL | Thumb
APPROVAL_COLS = dict(queued=0, caption=1, media=2, status=4, comment=5, thumb=8)

CALENDARS = {
    "Ola Digital": dict(
        sheet_id=os.environ.get("CONTENT_CALENDAR_SHEET_ID", "1fJ87Ho6r7FaL20JrxAMXM7LespS0qlvWZ_wVVhyKqsA"),
        date=0, time=1, caption=5, media=7, status=8, thumb=10,
        publishes="approved"),  # auto_post_from_calendar.py posts "approved" rows
    "Techno": dict(
        sheet_id=os.environ.get("TECHNO_CONTENT_CALENDAR_SHEET_ID", "1QTJ81L7WVFjOglHeUbOLAjKYrqoYxwym-mx8RzFKvEI"),
        date=0, time=1, caption=6, media=8, status=9, thumb=12,
        publishes="pending"),  # auto_post_techno.py posts "pending" rows, never "approved"
}

# Statuses that still need a human decision
OPEN_STATUSES = {"", "pending", "draft", "preview_sent"}


def col_letter(i: int) -> str:
    return chr(ord("A") + i)
