"""Cold Email page: generate, preview, and send personalized emails."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.cold_email import generate_cold_email, generate_followup
from app.core.config import PROJECT_ROOT, get_settings
from app.core.logging import setup_logging
from app.core.resume_parser import load_master_resume
from app.core.scheduler import get_scheduled_jobs, schedule_followup
from app.db import sqlite_cache as cache

setup_logging()
settings = get_settings()

st.title("Cold Email Outreach")

resume = load_master_resume()
if not resume:
    st.warning("Please upload your resume in Settings first.")
    st.stop()

jobs = cache.get_all_jobs()
if not jobs:
    st.info("No jobs in cache. Search for jobs first.")
    st.stop()

job_options = {f"{j['title']} @ {j['company']} ({j['source']})": j for j in jobs}
selected_label = st.selectbox("Select a job", options=list(job_options.keys()))
job = job_options[selected_label]

app = cache.get_application(job["id"])
recruiter_name = app.get("recruiter_name", "") if app else ""
recruiter_email = app.get("recruiter_email", "") if app else ""

st.subheader(f"Email for {job['title']} at {job['company']}")

if recruiter_email:
    st.success(f"Recruiter: {recruiter_name} ({recruiter_email})")
else:
    st.warning("No recruiter selected. Go to Find Recruiter page first.")
    recruiter_email = st.text_input("Or enter email manually:")

personalization_hook = st.text_input(
    "Personalization hook (company news, recruiter activity, etc.)",
    placeholder="e.g., Saw your post about scaling the data platform...",
)

attach_resume = st.checkbox("Attach resume PDF", value=False)

# ── Generate Email ────────────────────────────────────────────────────
if st.button("Generate Email", type="primary"):
    with st.spinner("Generating personalized email..."):
        try:
            result = generate_cold_email(
                resume=resume,
                jd_text=job.get("jd_text", ""),
                company=job["company"],
                job_title=job["title"],
                recruiter_name=recruiter_name,
                company_news=personalization_hook,
            )
            st.session_state["email_draft"] = result
        except Exception as e:
            st.error(f"Error: {e}")

if "email_draft" in st.session_state:
    draft = st.session_state["email_draft"]

    st.subheader("Email Preview")

    subject_choice = st.radio(
        "Choose subject line:",
        [draft.get("subject_a", ""), draft.get("subject_b", "")],
        key="subject_choice",
    )

    subject = st.text_input("Subject", value=subject_choice)
    body = st.text_area("Body", value=draft.get("body", ""), height=250)

    st.caption(f"To: {recruiter_email or 'Not set'}")
    st.caption(f"Word count: {len(body.split())}")

    can_spam = f"""
---
{settings.user_physical_address or '[Physical address required in .env]'}
To unsubscribe, reply with subject "unsubscribe"
"""
    st.text_area("CAN-SPAM Footer (auto-appended)", value=can_spam, disabled=True, height=80)

    st.markdown("---")

    if recruiter_email and st.button("Send Email", type="primary"):
        if not settings.gmail_oauth_client_id:
            st.error("Gmail OAuth not configured. Add GMAIL_OAUTH_CLIENT_ID to .env")
        else:
            with st.spinner("Sending via Gmail API..."):
                try:
                    from app.integrations.gmail import GmailClient

                    gmail = GmailClient()
                    body_html = body.replace("\n", "<br>")

                    attachments = []
                    if attach_resume:
                        resume_pdf = PROJECT_ROOT / "output" / f"{job['company']}_{job['id']}" / "resume.pdf"
                        if resume_pdf.exists():
                            attachments.append(str(resume_pdf))

                    result = gmail.send_email(
                        to=recruiter_email,
                        subject=subject,
                        body_html=body_html,
                        attachment_paths=attachments,
                    )

                    email_record = {
                        "job_id": job["id"],
                        "to_email": recruiter_email,
                        "to_name": recruiter_name,
                        "subject": subject,
                        "body": body,
                        "sent_at": datetime.utcnow().isoformat(),
                        "gmail_thread_id": result["thread_id"],
                        "gmail_message_id": result["message_id"],
                        "email_type": "cold",
                        "status": "sent",
                    }

                    if app:
                        app["status"] = "Email Sent"
                        app["thread_id"] = result["thread_id"]
                        app["last_email_at"] = datetime.utcnow().isoformat()
                        cache.upsert_application(app)

                    try:
                        from app.db.sheets import SheetsClient
                        sheets = SheetsClient()
                        sheets.append_email(email_record)
                        if app:
                            sheets.update_application(app)
                    except Exception:
                        pass

                    st.success(f"Email sent! Thread ID: {result['thread_id']}")
                    st.session_state["sent_thread_id"] = result["thread_id"]
                    st.session_state["sent_subject"] = subject

                except Exception as e:
                    st.error(f"Error sending email: {e}")

# ── Scheduled Jobs ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Scheduled Follow-ups & Jobs")
scheduled = get_scheduled_jobs()
if scheduled:
    for sj in scheduled:
        st.write(f"**{sj['name']}** — Next run: {sj['next_run']}")
else:
    st.info("No scheduled jobs.")
