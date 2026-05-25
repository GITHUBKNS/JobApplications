"""Resume tailoring page: ATS scoring and keyword optimization."""
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.ats_scorer import save_tailored_resume, score_resume, tailor_resume
from app.core.config import PROJECT_ROOT, get_settings
from app.core.logging import setup_logging
from app.core.pdf_renderer import render_resume_pdf
from app.core.resume_parser import load_master_resume
from app.db import sqlite_cache as cache

setup_logging()
settings = get_settings()

st.title("Resume Tailoring & ATS Scoring")

resume = load_master_resume()
if not resume:
    st.warning("Please upload and parse your resume in the Settings page first.")
    st.stop()

# ── Select Job ─────────────────────────────────────────────────────────
jobs = cache.get_all_jobs()
if not jobs:
    st.info("No jobs in cache. Search for jobs first.")
    st.stop()

job_options = {f"{j['title']} @ {j['company']} ({j['source']})": j for j in jobs}
selected_label = st.selectbox("Select a job to tailor for", options=list(job_options.keys()))
job = job_options[selected_label]

st.subheader(f"{job['title']} at {job['company']}")
if job.get("url"):
    st.markdown(f"[View Job Posting]({job['url']})")

with st.expander("Job Description"):
    st.text(job.get("jd_text", "No description available")[:3000])

# ── ATS Score ──────────────────────────────────────────────────────────
if st.button("Run ATS Analysis", type="primary"):
    with st.spinner("Analyzing resume against JD..."):
        try:
            analysis = score_resume(resume, job.get("jd_text", ""))

            st.subheader("ATS Score")
            col1, col2, col3 = st.columns(3)
            with col1:
                color = "green" if analysis.score >= 75 else "orange" if analysis.score >= 50 else "red"
                st.markdown(f"### :{color}[{analysis.score}/100]")
            with col2:
                st.metric("Matched Keywords", len(analysis.matched_keywords))
            with col3:
                st.metric("Missing Keywords", len(analysis.missing_keywords))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Matched Keywords:**")
                st.write(", ".join(analysis.matched_keywords) if analysis.matched_keywords else "None")

                st.markdown("**JD Skills:**")
                st.write(", ".join(analysis.jd_skills) if analysis.jd_skills else "None")
            with col2:
                st.markdown("**Missing Keywords:**")
                st.write(", ".join(analysis.missing_keywords) if analysis.missing_keywords else "None")

                st.markdown("**JD Tools:**")
                st.write(", ".join(analysis.jd_tools) if analysis.jd_tools else "None")

            if analysis.suggestions:
                st.markdown("**Suggestions:**")
                for s in analysis.suggestions:
                    st.markdown(f"- {s}")

            st.session_state["ats_analysis"] = analysis
        except Exception as e:
            st.error(f"Error: {e}")

# ── Tailor Resume ──────────────────────────────────────────────────────
st.markdown("---")
if st.button("Generate Tailored Resume"):
    with st.spinner("Tailoring resume with AI... This may take 30-60 seconds."):
        try:
            tailored = tailor_resume(resume, job.get("jd_text", ""))

            st.subheader("Before / After Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Bullets:**")
                for exp in resume.experience:
                    st.markdown(f"*{exp.title} at {exp.company}*")
                    for b in exp.bullets:
                        st.markdown(f"- {b}")

            with col2:
                st.markdown("**Tailored Bullets:**")
                for exp in tailored.experience:
                    st.markdown(f"*{exp.title} at {exp.company}*")
                    for b in exp.bullets:
                        st.markdown(f"- {b}")

            st.session_state["tailored_resume"] = tailored

            json_path = save_tailored_resume(tailored, job["company"], job["id"])
            st.success(f"Tailored resume JSON saved to {json_path}")

        except Exception as e:
            st.error(f"Error: {e}")

# ── Render PDF ────────────────────────────────────────────────────────
if "tailored_resume" in st.session_state:
    st.markdown("---")
    if st.button("Render PDF"):
        with st.spinner("Rendering PDF..."):
            try:
                tailored = st.session_state["tailored_resume"]
                output_dir = PROJECT_ROOT / "output" / f"{job['company']}_{job['id']}"
                pdf_path = output_dir / "resume.pdf"
                render_resume_pdf(tailored, pdf_path)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "Download Tailored Resume PDF",
                        data=f.read(),
                        file_name=f"resume_{job['company']}.pdf",
                        mime="application/pdf",
                    )
                st.success(f"PDF saved to {pdf_path}")
            except Exception as e:
                st.error(f"Error rendering PDF: {e}")
