"""Local SQLite cache for fast lookups. Google Sheets remains system of record."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from app.core.config import PROJECT_ROOT
from app.core.logging import get_logger

log = get_logger(__name__)

DB_PATH = PROJECT_ROOT / "cache.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    remote INTEGER DEFAULT 0,
    posted_at TEXT,
    source TEXT,
    url TEXT,
    jd_text TEXT,
    salary TEXT,
    visa_signal TEXT,
    company_domain TEXT,
    raw_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS applications (
    job_id TEXT PRIMARY KEY,
    company TEXT,
    title TEXT,
    status TEXT DEFAULT 'Saved',
    applied_at TEXT,
    resume_path TEXT,
    cover_letter_path TEXT,
    recruiter_name TEXT,
    recruiter_email TEXT,
    thread_id TEXT,
    last_email_at TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    to_email TEXT,
    to_name TEXT,
    subject TEXT,
    body TEXT,
    sent_at TEXT,
    gmail_thread_id TEXT,
    gmail_message_id TEXT,
    email_type TEXT DEFAULT 'cold',
    status TEXT DEFAULT 'sent',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cache_kv (
    key TEXT PRIMARY KEY,
    value TEXT,
    expires_at TEXT
);
"""


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(SCHEMA)
    log.info("sqlite_initialized", path=str(DB_PATH))


def upsert_job(job: dict) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO jobs
               (id, title, company, location, remote, posted_at, source, url,
                jd_text, salary, visa_signal, company_domain, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job["id"], job["title"], job["company"], job.get("location", ""),
                int(job.get("remote", False)), job.get("posted_at", ""),
                job.get("source", ""), job.get("url", ""), job.get("jd_text", ""),
                job.get("salary", ""), job.get("visa_sponsorship_signal", ""),
                job.get("company_domain", ""),
                json.dumps(job.get("raw_data", {})),
            ),
        )


def get_all_jobs() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def upsert_application(app: dict) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO applications
               (job_id, company, title, status, applied_at, resume_path,
                cover_letter_path, recruiter_name, recruiter_email,
                thread_id, last_email_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                app["job_id"], app["company"], app["title"],
                app.get("status", "Saved"), app.get("applied_at", ""),
                app.get("resume_path", ""), app.get("cover_letter_path", ""),
                app.get("recruiter_name", ""), app.get("recruiter_email", ""),
                app.get("thread_id", ""), app.get("last_email_at", ""),
                app.get("notes", ""),
            ),
        )


def get_application(job_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE job_id = ?", (job_id,)
        ).fetchone()
        return dict(row) if row else None


def set_cache(key: str, value: Any, ttl_seconds: int = 86400) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO cache_kv (key, value, expires_at)
               VALUES (?, ?, datetime('now', '+' || ? || ' seconds'))""",
            (key, json.dumps(value), ttl_seconds),
        )


def get_cache(key: str) -> Any | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT value FROM cache_kv WHERE key = ? AND expires_at > datetime('now')",
            (key,),
        ).fetchone()
        return json.loads(row["value"]) if row else None


init_db()
