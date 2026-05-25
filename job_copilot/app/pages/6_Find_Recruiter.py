"""Find Recruiter page: discover and verify recruiter emails."""
import asyncio
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.recruiter_finder import find_recruiters, verify_recruiter_email
from app.db import sqlite_cache as cache

setup_logging()
settings = get_settings()

st.title("Find Recruiter")

jobs = cache.get_all_jobs()
if not jobs:
    st.info("No jobs in cache. Search for jobs first.")
    st.stop()

job_options = {f"{j['title']} @ {j['company']} ({j['source']})": j for j in jobs}
selected_label = st.selectbox("Select a job", options=list(job_options.keys()))
job = job_options[selected_label]

st.subheader(f"Finding recruiters for {job['company']}")

company_domain = st.text_input(
    "Company domain",
    value=job.get("company_domain", "").replace("https://", "").replace("http://", "").split("/")[0],
    placeholder="e.g., stripe.com",
)

if st.button("Search for Recruiters", type="primary"):
    with st.spinner("Searching across Hunter, Apollo, RocketReach..."):
        try:
            candidates = asyncio.run(
                find_recruiters(
                    company=job["company"],
                    company_domain=company_domain,
                    jd_text=job.get("jd_text", ""),
                )
            )

            if not candidates:
                st.warning("No recruiters found. Try a different company domain.")
            else:
                st.session_state["recruiter_candidates"] = candidates
                st.success(f"Found {len(candidates)} potential recruiter(s)")
        except Exception as e:
            st.error(f"Error: {e}")

if "recruiter_candidates" in st.session_state:
    candidates = st.session_state["recruiter_candidates"]

    for i, c in enumerate(candidates[:10]):
        conf_pct = f"{c.confidence * 100:.0f}%"
        verified_badge = " (Verified)" if c.verified else ""

        with st.expander(f"{c.name or 'Unknown'} — {c.title} — Confidence: {conf_pct}{verified_badge}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Email:** {c.email or 'Not found'}")
                st.write(f"**Source:** {c.source}")
            with col2:
                st.write(f"**Company:** {c.company}")
                if c.linkedin_url:
                    st.markdown(f"[LinkedIn]({c.linkedin_url})")

            if c.email and not c.verified:
                if st.button(f"Verify Email", key=f"verify_{i}"):
                    with st.spinner("Verifying..."):
                        verified_c = asyncio.run(verify_recruiter_email(c))
                        candidates[i] = verified_c
                        st.session_state["recruiter_candidates"] = candidates
                        if verified_c.verified:
                            st.success(f"Email verified: {verified_c.verification_result}")
                        else:
                            st.warning(f"Verification result: {verified_c.verification_result}")

            if st.button("Select This Recruiter", key=f"select_{i}"):
                app = cache.get_application(job["id"])
                if app:
                    app["recruiter_name"] = c.name
                    app["recruiter_email"] = c.email
                    cache.upsert_application(app)
                else:
                    cache.upsert_application({
                        "job_id": job["id"],
                        "company": job["company"],
                        "title": job["title"],
                        "recruiter_name": c.name,
                        "recruiter_email": c.email,
                    })
                st.success(f"Selected {c.name} ({c.email}) as recruiter for this job!")
