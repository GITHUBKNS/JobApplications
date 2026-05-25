"""Gmail API integration via OAuth2 for sending emails and tracking threads."""
from __future__ import annotations

import base64
import json
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._service = None

    def _get_credentials(self) -> Credentials:
        token_path = self._settings.gmail_token_full_path
        creds = None

        if token_path.exists():
            creds_data = json.loads(token_path.read_text())
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
            return creds

        if not self._settings.gmail_oauth_client_id:
            raise RuntimeError("Gmail OAuth client ID not configured")

        client_config = {
            "installed": {
                "client_id": self._settings.gmail_oauth_client_id,
                "client_secret": self._settings.gmail_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        return creds

    def _get_service(self):
        if self._service is None:
            creds = self._get_credentials()
            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def send_email(
        self,
        to: str,
        subject: str,
        body_html: str,
        thread_id: str = "",
        attachment_paths: list[str] | None = None,
        physical_address: str = "",
    ) -> dict:
        """Send an email via Gmail API. Returns {thread_id, message_id}."""
        service = self._get_service()

        if not physical_address:
            physical_address = self._settings.user_physical_address

        can_spam_footer = f"""
<br><br>
<hr style="border:none;border-top:1px solid #ccc;margin:20px 0;">
<p style="font-size:11px;color:#999;">
{physical_address}<br>
<a href="mailto:{to}?subject=unsubscribe">Unsubscribe</a>
</p>
"""
        body_html += can_spam_footer

        if attachment_paths:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body_html, "html"))
            for fpath in attachment_paths:
                p = Path(fpath)
                if p.exists():
                    with open(p, "rb") as f:
                        part = MIMEApplication(f.read(), Name=p.name)
                    part["Content-Disposition"] = f'attachment; filename="{p.name}"'
                    msg.attach(part)
        else:
            msg = MIMEText(body_html, "html")

        msg["to"] = to
        msg["subject"] = subject
        msg["from"] = self._settings.user_email or "me"

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        body: dict = {"raw": raw}
        if thread_id:
            body["threadId"] = thread_id

        result = service.users().messages().send(userId="me", body=body).execute()
        log.info("gmail_sent", to=to, subject=subject, message_id=result.get("id"))
        return {
            "thread_id": result.get("threadId", ""),
            "message_id": result.get("id", ""),
        }

    def check_for_replies(self, thread_id: str) -> bool:
        """Check if there are replies (from others) in a Gmail thread."""
        if not thread_id:
            return False
        service = self._get_service()
        try:
            thread = service.users().threads().get(userId="me", id=thread_id).execute()
            messages = thread.get("messages", [])
            if len(messages) <= 1:
                return False
            my_email = self._settings.user_email
            for msg in messages[1:]:
                headers = msg.get("payload", {}).get("headers", [])
                from_header = next(
                    (h["value"] for h in headers if h["name"].lower() == "from"), ""
                )
                if my_email and my_email.lower() not in from_header.lower():
                    return True
            return False
        except Exception as e:
            log.error("gmail_reply_check_error", thread_id=thread_id, error=str(e))
            return False
