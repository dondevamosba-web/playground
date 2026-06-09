"""
Gmail API wrapper for creating drafts programmatically.
Uses token_gmail.json (gmail.compose scope) — separate from the Drive token.

Usage:
    from tools.gmail_draft import create_draft, build_html_body
    draft_id = create_draft("to@example.com", "Subject", "Body text")
    draft_id = create_draft("to@example.com", "Subject", html_body, html=True)

First run: opens browser OAuth flow to authorize gmail.compose scope.
Subsequent runs: uses saved token (auto-refreshes).
"""

import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
_BASE = os.path.dirname(__file__)
TOKEN_PATH = os.path.join(_BASE, "..", "token_gmail.json")
CREDS_PATH = os.path.join(_BASE, "..", "credentials.json")

SIGNATURE_HTML = """
<div style="margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <p style="margin:0;font-size:14px;font-weight:600;color:#0E1116;">Guido Carminatti</p>
  <p style="margin:4px 0 0;font-size:13px;color:#6b7280;">
    <a href="https://stormdigitalhq.netlify.app" style="color:#E8420A;text-decoration:none;">Storm Digital</a>
    &nbsp;&middot;&nbsp;
    <a href="https://cal.com/guido-carminatti-wvudqi/demo" style="color:#6b7280;text-decoration:none;">Book a free call</a>
  </p>
</div>
"""


PRICING_HTML = """
<div style="margin-top:20px;margin-bottom:4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table style="border-collapse:collapse;width:100%;max-width:480px;font-size:13px;">
    <thead>
      <tr style="background:#0E1116;color:#fff;">
        <th style="padding:8px 12px;text-align:left;font-weight:600;">Plan</th>
        <th style="padding:8px 12px;text-align:left;font-weight:600;">Monthly Fee</th>
        <th style="padding:8px 12px;text-align:left;font-weight:600;">Leads/Month</th>
      </tr>
    </thead>
    <tbody>
      <tr style="background:#f9f9f9;">
        <td style="padding:8px 12px;">Starter</td>
        <td style="padding:8px 12px;">$997</td>
        <td style="padding:8px 12px;">10–15 exclusive</td>
      </tr>
      <tr>
        <td style="padding:8px 12px;">Growth</td>
        <td style="padding:8px 12px;">$1,497</td>
        <td style="padding:8px 12px;">20–30 exclusive</td>
      </tr>
      <tr style="background:#f9f9f9;">
        <td style="padding:8px 12px;">Scale</td>
        <td style="padding:8px 12px;">$2,497</td>
        <td style="padding:8px 12px;">40–60 exclusive</td>
      </tr>
    </tbody>
  </table>
  <p style="margin:8px 0 0;font-size:12px;color:#6b7280;">Month-to-month. If we don't hit your lead target in 60 days, we work free until we do.</p>
</div>
"""


def build_html_body(plain_text: str, include_pricing: bool = False) -> str:
    """Wrap plain text body with optional pricing table and HTML signature."""
    paragraphs = "".join(
        f"<p style='margin:0 0 12px;'>{line}</p>" if line.strip() else "<br>"
        for line in plain_text.strip().splitlines()
    )
    pricing_block = PRICING_HTML if include_pricing else ""
    return f"""<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;line-height:1.6;color:#0E1116;">
{paragraphs}
{pricing_block}
{SIGNATURE_HTML}
</div>"""


def _get_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def create_draft(to: str, subject: str, body: str, html: bool = False, label_ids: list = None) -> dict:
    """
    Create a Gmail draft and optionally apply labels.
    Pass html=True to send an HTML email (use build_html_body to generate the body).
    Returns {"draft_id": ..., "message_id": ...}
    """
    service = _get_service()

    if html:
        msg = MIMEMultipart("alternative")
        msg["to"] = to
        msg["subject"] = subject
        msg.attach(MIMEText(body, "html", "utf-8"))
    else:
        msg = MIMEText(body, "plain", "utf-8")
        msg["to"] = to
        msg["subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    message_id = draft["message"]["id"]

    if label_ids:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": label_ids}
        ).execute()

    return {"draft_id": draft["id"], "message_id": message_id}


if __name__ == "__main__":
    html_body = build_html_body("If you see this, the Gmail API is working correctly.\n\nFormatting looks good.")
    result = create_draft(
        to="dondevamosba@gmail.com",
        subject="Gmail API test",
        body=html_body,
        html=True,
    )
    print(f"Draft created: {result}")
