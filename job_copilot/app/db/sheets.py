"""Google Sheets adapter — system of record for all application data."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_TITLE = "Job Application Tracker"

TAB_SCHEMAS = {
    "Jobs": [
        "id", "title", "company", "location", "remote", "posted_at",
        "source", "url", "salary", "visa_signal", "discovered_at",
    ],
    "Applications": [
        "job_id", "company", "title", "status", "applied_at",
        "resume_path", "cover_letter_path", "recruiter_name",
        "recruiter_email", "thread_id", "last_email_at", "notes",
    ],
    "Emails": [
        "job_id", "to_email", "to_name", "subject", "body",
        "sent_at", "gmail_thread_id", "gmail_message_id",
        "email_type", "status",
    ],
    "Followups": [
        "job_id", "email_type", "scheduled_at", "sent_at",
        "cancelled", "cancel_reason",
    ],
    "Analytics": [
        "metric", "value", "updated_at",
    ],
    "Errors": [
        "timestamp", "component", "error", "details",
    ],
}


class SheetsClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._gc: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None

    def _connect(self) -> gspread.Client:
        if self._gc is not None:
            return self._gc
        sa_path = self._settings.service_account_path
        if not sa_path.exists():
            raise FileNotFoundError(
                f"Google service account file not found at {sa_path}. "
                "Add it to secrets/service_account.json"
            )
        creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
        self._gc = gspread.authorize(creds)
        return self._gc

    def get_or_create_spreadsheet(self) -> gspread.Spreadsheet:
        if self._spreadsheet is not None:
            return self._spreadsheet
        gc = self._connect()
        try:
            self._spreadsheet = gc.open(SPREADSHEET_TITLE)
            log.info("sheets_opened", title=SPREADSHEET_TITLE)
        except gspread.SpreadsheetNotFound:
            self._spreadsheet = gc.create(SPREADSHEET_TITLE)
            log.info("sheets_created", title=SPREADSHEET_TITLE)
        self._ensure_tabs()
        return self._spreadsheet

    def _ensure_tabs(self) -> None:
        ss = self._spreadsheet
        existing = {ws.title for ws in ss.worksheets()}
        for tab_name, headers in TAB_SCHEMAS.items():
            if tab_name not in existing:
                ws = ss.add_worksheet(title=tab_name, rows=1000, cols=len(headers))
                ws.update("A1", [headers])
                log.info("sheets_tab_created", tab=tab_name)
            else:
                ws = ss.worksheet(tab_name)
                first_row = ws.row_values(1)
                if first_row != headers:
                    ws.update("A1", [headers])
        # Remove default Sheet1 if it exists and is empty
        if "Sheet1" in existing:
            try:
                sheet1 = ss.worksheet("Sheet1")
                if not sheet1.get_all_values()[1:]:
                    ss.del_worksheet(sheet1)
            except Exception:
                pass

    @property
    def url(self) -> str:
        ss = self.get_or_create_spreadsheet()
        return ss.url

    def append_job(self, job: dict) -> None:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Jobs")
        existing_ids = ws.col_values(1)[1:]
        if job.get("id") in existing_ids:
            return
        row = [
            job.get("id", ""), job.get("title", ""), job.get("company", ""),
            job.get("location", ""), str(job.get("remote", False)),
            str(job.get("posted_at", "")), job.get("source", ""),
            job.get("url", ""), job.get("salary", ""),
            job.get("visa_sponsorship_signal", ""),
            datetime.utcnow().isoformat(),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")

    def append_application(self, app: dict) -> None:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Applications")
        existing_ids = ws.col_values(1)[1:]
        if app.get("job_id") in existing_ids:
            self.update_application(app)
            return
        row = [
            app.get("job_id", ""), app.get("company", ""), app.get("title", ""),
            app.get("status", "Saved"), app.get("applied_at", ""),
            app.get("resume_path", ""), app.get("cover_letter_path", ""),
            app.get("recruiter_name", ""), app.get("recruiter_email", ""),
            app.get("thread_id", ""), app.get("last_email_at", ""),
            app.get("notes", ""),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")

    def update_application(self, app: dict) -> None:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Applications")
        job_ids = ws.col_values(1)
        try:
            row_idx = job_ids.index(app["job_id"]) + 1
        except ValueError:
            self.append_application(app)
            return
        row = [
            app.get("job_id", ""), app.get("company", ""), app.get("title", ""),
            app.get("status", "Saved"), app.get("applied_at", ""),
            app.get("resume_path", ""), app.get("cover_letter_path", ""),
            app.get("recruiter_name", ""), app.get("recruiter_email", ""),
            app.get("thread_id", ""), app.get("last_email_at", ""),
            app.get("notes", ""),
        ]
        ws.update(f"A{row_idx}", [row], value_input_option="USER_ENTERED")

    def append_email(self, email: dict) -> None:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Emails")
        row = [
            email.get("job_id", ""), email.get("to_email", ""),
            email.get("to_name", ""), email.get("subject", ""),
            email.get("body", ""), email.get("sent_at", ""),
            email.get("gmail_thread_id", ""), email.get("gmail_message_id", ""),
            email.get("email_type", "cold"), email.get("status", "sent"),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")

    def append_followup(self, followup: dict) -> None:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Followups")
        row = [
            followup.get("job_id", ""), followup.get("email_type", ""),
            followup.get("scheduled_at", ""), followup.get("sent_at", ""),
            str(followup.get("cancelled", False)),
            followup.get("cancel_reason", ""),
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")

    def log_error(self, component: str, error: str, details: str = "") -> None:
        try:
            ss = self.get_or_create_spreadsheet()
            ws = ss.worksheet("Errors")
            ws.append_row(
                [datetime.utcnow().isoformat(), component, error, details],
                value_input_option="USER_ENTERED",
            )
        except Exception:
            log.error("failed_to_log_error_to_sheets", component=component, error=error)

    def get_all_jobs(self) -> list[dict]:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Jobs")
        records = ws.get_all_records()
        return records

    def get_all_applications(self) -> list[dict]:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Applications")
        return ws.get_all_records()

    def get_all_emails(self) -> list[dict]:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Emails")
        return ws.get_all_records()

    def get_all_followups(self) -> list[dict]:
        ss = self.get_or_create_spreadsheet()
        ws = ss.worksheet("Followups")
        return ws.get_all_records()
