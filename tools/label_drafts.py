"""
Bulk-label Storm Digital outreach drafts by subject pattern.

Labels applied:
  Label_9  = Roofing - Ads Angle      ("your ads")
  Label_10 = Roofing - Lead Flow Angle ("roofing leads", "lead flow")
  Label_11 = HVAC - Lead Flow Angle    ("HVAC leads", "HVAC leads exclusive")

Run once to tag all un-labeled agency outreach drafts.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gmail_draft import _get_service

RULES = [
    ("hvac leads", "Label_11"),
    ("hvac leads exclusive", "Label_11"),
    ("plumbing leads", "Label_12"),
    ("your plumbing leads", "Label_12"),
    ("window leads", "Label_13"),
    ("your window leads", "Label_13"),
    ("roofing leads", "Label_10"),
    ("lead flow", "Label_10"),
    ("your ads", "Label_9"),
]


def classify(subject: str):
    s = subject.lower()
    for pattern, label_id in RULES:
        if pattern in s:
            return label_id
    return None


def run():
    service = _get_service()
    page_token = None
    total = 0
    labeled = 0

    while True:
        kwargs = {"userId": "me", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token

        resp = service.users().drafts().list(**kwargs).execute()
        drafts = resp.get("drafts", [])

        for d in drafts:
            detail = service.users().drafts().get(
                userId="me", id=d["id"], format="metadata"
            ).execute()
            headers = detail.get("message", {}).get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
            msg_id = detail["message"]["id"]

            label_id = classify(subject)
            if label_id:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"addLabelIds": [label_id]}
                ).execute()
                labeled += 1
                print(f"  [{label_id}] {subject[:60]}")
            total += 1

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(f"\nDone. {labeled}/{total} drafts labeled.")


if __name__ == "__main__":
    run()
