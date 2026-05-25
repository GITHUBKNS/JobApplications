"""Search Jobs page with saved filters and multi-source discovery."""
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import get_settings
from app.core.job_discovery import run_discovery_sync
from app.core.logging import setup_logging
from app.core.visa_classifier import classify_visa_signal
from app.db import sqlite_cache as cache
from app.models.schemas import JobPosting

setup_logging()
settings = get_settings()

st.title("Search Jobs")

# ── Filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Search Filters")
    keywords = st.text_area(
        "Keywords (one per line)",
        value="Data Engineer\nAnalytics Engineer",
        height=80,
    )
    locations = st.text_area(
        "Locations (one per line)",
        value="Newark, NJ\nRemote\nUnited States",
        height=80,
    )
    posted_within = st.slider("Posted within (days)", 1, 30, 7)
    require_visa = st.checkbox("Require visa sponsorship", value=True)
    salary_floor = st.number_input("Minimum salary ($)", min_value=0, value=0, step=10000)
    ats_companies = st.text_area(
        "ATS Companies to check (slugs, one per line)",
        value="stripe\ndatadog\nfigma\nnotion\nreddit\ncoinbase\nramp\ndatabricks\nsnowflake",
        height=120,
    )

# ── Search ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 3])
with col1:
    search_btn = st.button("Search Now", type="primary")
with col2:
    use_cache = st.checkbox("Show cached results first", value=True)

if use_cache and not search_btn:
    cached_jobs = cache.get_all_jobs()
    if cached_jobs:
        st.info(f"Showing {len(cached_jobs)} cached jobs. Click 'Search Now' to fetch fresh results.")
        for job in cached_jobs[:50]:
            visa = job.get("visa_signal", "unknown")
            visa_badge = {"reject": "🔴", "positive": "🟢", "unknown": "🟡"}.get(visa, "🟡")

            with st.expander(f"{visa_badge} {job['title']} @ {job['company']} ({job['source']})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Location:** {job.get('location', 'N/A')}")
                with col2:
                    st.write(f"**Remote:** {'Yes' if job.get('remote') else 'No'}")
                with col3:
                    st.write(f"**Salary:** {job.get('salary', 'N/A') or 'N/A'}")

                if job.get("url"):
                    st.markdown(f"[View Job]({job['url']})")

                if job.get("jd_text"):
                    st.text_area("Job Description", value=job["jd_text"][:2000], height=200, key=f"jd_{job['id']}", disabled=True)

                if st.button("Save for Application", key=f"save_{job['id']}"):
                    from app.db.sqlite_cache import upsert_application
                    upsert_application({
                        "job_id": job["id"],
                        "company": job["company"],
                        "title": job["title"],
                        "status": "Saved",
                    })
                    st.success("Job saved!")
    else:
        st.info("No cached jobs. Click 'Search Now' to discover jobs.")

if search_btn:
    kw_list = [k.strip() for k in keywords.split("\n") if k.strip()]
    loc_list = [l.strip() for l in locations.split("\n") if l.strip()]
    ats_list = [c.strip() for c in ats_companies.split("\n") if c.strip()]

    with st.spinner("Searching across all sources... This may take 30-60 seconds."):
        try:
            jobs = run_discovery_sync(
                keywords=kw_list,
                locations=loc_list,
                posted_within_days=posted_within,
                require_visa_sponsorship=require_visa,
                salary_floor=salary_floor if salary_floor > 0 else None,
                ats_companies=ats_list,
            )

            if not jobs:
                st.warning("No jobs found matching your criteria.")
            else:
                st.success(f"Found {len(jobs)} unique jobs!")

                for job in jobs:
                    visa = job.visa_sponsorship_signal or "unknown"
                    visa_badge = {"reject": "🔴", "positive": "🟢", "unknown": "🟡"}.get(visa, "🟡")

                    with st.expander(f"{visa_badge} {job.title} @ {job.company} ({job.source})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Location:** {job.location}")
                        with col2:
                            st.write(f"**Remote:** {'Yes' if job.remote else 'No'}")
                        with col3:
                            st.write(f"**Salary:** {job.salary or 'N/A'}")

                        if job.posted_at:
                            st.write(f"**Posted:** {job.posted_at.strftime('%Y-%m-%d')}")
                        if job.url:
                            st.markdown(f"[View Job]({job.url})")

                        if job.jd_text:
                            st.text_area(
                                "Job Description",
                                value=job.jd_text[:2000],
                                height=200,
                                key=f"jd_{job.id}",
                                disabled=True,
                            )

                        if st.button("Save for Application", key=f"save_{job.id}"):
                            cache.upsert_application({
                                "job_id": job.id,
                                "company": job.company,
                                "title": job.title,
                                "status": "Saved",
                            })
                            st.success("Job saved!")

        except Exception as e:
            st.error(f"Error during search: {e}")
