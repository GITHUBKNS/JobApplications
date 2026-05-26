"""Apply page: autofill payload, open job URL, mark as applied."""
import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.autofill import format_autofill_clipboard, generate_autofill
from app.core.config import PROJECT_ROOT, get_settings
from app.core.logging import setup_logging
from app.core.resume_parser import load_master_resume
from app.db import sqlite_cache as cache

setup_logging()
settings = get_settings()

st.title("Apply to Jobs")

resume = load_master_resume()
if not resume:
    st.warning("Please upload your resume in Settings first.")
    st.stop()

jobs = cache.get_all_jobs()
if not jobs:
    st.info("No jobs in cache. Search for jobs first.")
    st.stop()

job_options = {f"{j['title']} @ {j['company']} ({j['source']})": j for j in jobs}
selected_label = st.selectbox("Select a job to apply", options=list(job_options.keys()))
job = job_options[selected_label]

st.subheader(f"{job['title']} at {job['company']}")

# Check for existing files
output_dir = PROJECT_ROOT / "output" / f"{job['company']}_{job['id']}"
resume_pdf = output_dir / "resume.pdf"
cover_letter_pdf = output_dir / "cover_letter.pdf"

col1, col2 = st.columns(2)
with col1:
    if resume_pdf.exists():
        st.success("Tailored resume PDF ready")
        with open(resume_pdf, "rb") as f:
            st.download_button("Download Resume", f.read(), f"resume_{job['company']}.pdf", "application/pdf")
    else:
        st.info("No tailored resume yet. Generate one in Resume Tailoring page.")

with col2:
    if cover_letter_pdf.exists():
        st.success("Cover letter PDF ready")
        with open(cover_letter_pdf, "rb") as f:
            st.download_button("Download Cover Letter", f.read(), f"cover_{job['company']}.pdf", "application/pdf")
    else:
        st.info("No cover letter yet. Generate one in Cover Letter page.")

# ── Autofill Payload ──────────────────────────────────────────────────
st.subheader("Autofill Payload")

if st.button("Generate Autofill"):
    payload = generate_autofill(resume)
    st.session_state["autofill_payload"] = payload

if "autofill_payload" in st.session_state:
    payload = st.session_state["autofill_payload"]
    clipboard_text = format_autofill_clipboard(payload)
    st.text_area("Copy this to clipboard:", value=clipboard_text, height=300)
    st.json(payload.model_dump())

# ── Open Job & Mark Applied ──────────────────────────────────────────
st.markdown("---")
st.subheader("Apply")

if job.get("url"):
    st.markdown(f"### [Open Application Page]({job['url']})")
    st.caption("Opens in a new tab. The app will NOT auto-submit — you apply manually.")

if st.button("Mark as Applied", type="primary"):
    app_data = {
        "job_id": job["id"],
        "company": job["company"],
        "title": job["title"],
        "status": "Applied",
        "applied_at": datetime.utcnow().isoformat(),
        "resume_path": str(resume_pdf) if resume_pdf.exists() else "",
        "cover_letter_path": str(cover_letter_pdf) if cover_letter_pdf.exists() else "",
    }
    cache.upsert_application(app_data)

    try:
        from app.db.sheets import SheetsClient
        sheets = SheetsClient()
        sheets.append_application(app_data)
    except Exception:
        pass

    st.success("Marked as Applied!")
    st.balloons()
