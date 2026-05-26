"""Cover letter generation page."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import PROJECT_ROOT, get_settings
from app.core.cover_letter import generate_cover_letter, save_cover_letter
from app.core.logging import setup_logging
from app.core.pdf_renderer import render_cover_letter_pdf
from app.core.resume_parser import load_master_resume
from app.db import sqlite_cache as cache

setup_logging()
settings = get_settings()

st.title("Cover Letter Generator")

resume = load_master_resume()
if not resume:
    st.warning("Please upload and parse your resume in Settings first.")
    st.stop()

jobs = cache.get_all_jobs()
if not jobs:
    st.info("No jobs in cache. Search for jobs first.")
    st.stop()

job_options = {f"{j['title']} @ {j['company']} ({j['source']})": j for j in jobs}
selected_label = st.selectbox("Select a job", options=list(job_options.keys()))
job = job_options[selected_label]

st.subheader(f"{job['title']} at {job['company']}")

company_news = st.text_input(
    "Company news / personalization hook (optional)",
    placeholder="e.g., Company just raised Series C, launched new data platform...",
)

recruiter_name = st.text_input("Recruiter name (optional)", placeholder="e.g., Jane Smith")

if st.button("Generate Cover Letter", type="primary"):
    with st.spinner("Generating cover letter..."):
        try:
            letter = generate_cover_letter(
                resume=resume,
                jd_text=job.get("jd_text", ""),
                company=job["company"],
                job_title=job["title"],
                company_news=company_news,
                recruiter_name=recruiter_name,
            )
            st.session_state["cover_letter"] = letter
            st.session_state["cover_letter_job"] = job
        except Exception as e:
            st.error(f"Error: {e}")

if "cover_letter" in st.session_state:
    st.subheader("Generated Cover Letter")
    edited = st.text_area(
        "Edit cover letter below:",
        value=st.session_state["cover_letter"],
        height=400,
    )
    st.session_state["cover_letter"] = edited

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save as Text"):
            cl_job = st.session_state["cover_letter_job"]
            path = save_cover_letter(edited, cl_job["company"], cl_job["id"])
            st.success(f"Saved to {path}")

    with col2:
        if st.button("Render PDF"):
            with st.spinner("Rendering PDF..."):
                try:
                    cl_job = st.session_state["cover_letter_job"]
                    output_dir = PROJECT_ROOT / "output" / f"{cl_job['company']}_{cl_job['id']}"
                    pdf_path = output_dir / "cover_letter.pdf"
                    render_cover_letter_pdf(
                        text=edited,
                        candidate_name=resume.contact.name or settings.user_name,
                        company=cl_job["company"],
                        job_title=cl_job["title"],
                        output_path=pdf_path,
                    )
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "Download Cover Letter PDF",
                            data=f.read(),
                            file_name=f"cover_letter_{cl_job['company']}.pdf",
                            mime="application/pdf",
                        )
                    st.success(f"PDF saved to {pdf_path}")
                except Exception as e:
                    st.error(f"Error: {e}")
