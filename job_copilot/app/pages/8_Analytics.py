"""Analytics page: application funnel, response rates, charts."""
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db import sqlite_cache as cache
from app.models.schemas import ApplicationStatus

setup_logging()
settings = get_settings()

st.title("Analytics Dashboard")

# ── Data Source Toggle ─────────────────────────────────────────────────
data_source = st.radio("Data source", ["Local Cache (SQLite)", "Google Sheets"], horizontal=True)

if data_source == "Google Sheets":
    try:
        from app.db.sheets import SheetsClient
        sheets = SheetsClient()
        applications = sheets.get_all_applications()
        emails = sheets.get_all_emails()
        jobs = sheets.get_all_jobs()
    except Exception as e:
        st.error(f"Could not connect to Sheets: {e}")
        st.info("Falling back to local cache.")
        data_source = "Local Cache (SQLite)"

if data_source == "Local Cache (SQLite)":
    from app.db.sqlite_cache import get_all_jobs, get_db
    jobs = get_all_jobs()

    with get_db() as conn:
        app_rows = conn.execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()
        applications = [dict(r) for r in app_rows]
        email_rows = conn.execute("SELECT * FROM emails ORDER BY created_at DESC").fetchall()
        emails = [dict(r) for r in email_rows]

# ── Summary Metrics ───────────────────────────────────────────────────
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Jobs Discovered", len(jobs))
with col2:
    st.metric("Applications", len(applications))
with col3:
    st.metric("Emails Sent", len(emails))
with col4:
    replied = sum(1 for a in applications if a.get("status") == "Recruiter Replied")
    st.metric("Replies Received", replied)

# ── Status Distribution ──────────────────────────────────────────────
if applications:
    st.subheader("Application Status Distribution")
    status_counts = Counter(a.get("status", "Unknown") for a in applications)

    fig = px.pie(
        names=list(status_counts.keys()),
        values=list(status_counts.values()),
        title="Applications by Status",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Funnel Chart ─────────────────────────────────────────────────
    st.subheader("Application Funnel")
    funnel_stages = [s.value for s in ApplicationStatus]
    funnel_counts = [status_counts.get(s, 0) for s in funnel_stages]

    non_zero_stages = [(s, c) for s, c in zip(funnel_stages, funnel_counts) if c > 0]
    if non_zero_stages:
        fig_funnel = go.Figure(go.Funnel(
            y=[s for s, _ in non_zero_stages],
            x=[c for _, c in non_zero_stages],
            textinfo="value+percent initial",
        ))
        fig_funnel.update_layout(title="Application Funnel")
        st.plotly_chart(fig_funnel, use_container_width=True)

    # ── Applications Per Week ────────────────────────────────────────
    st.subheader("Applications Per Week")
    weekly_counts: dict[str, int] = {}
    for a in applications:
        applied = a.get("applied_at", "") or a.get("created_at", "")
        if applied:
            try:
                dt = datetime.fromisoformat(applied.replace("Z", "+00:00")) if "T" in applied else datetime.strptime(applied, "%Y-%m-%d")
                week = dt.strftime("%Y-W%U")
                weekly_counts[week] = weekly_counts.get(week, 0) + 1
            except (ValueError, TypeError):
                pass

    if weekly_counts:
        sorted_weeks = sorted(weekly_counts.items())
        fig_weekly = px.bar(
            x=[w for w, _ in sorted_weeks],
            y=[c for _, c in sorted_weeks],
            labels={"x": "Week", "y": "Applications"},
            title="Applications Per Week",
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

    # ── Response Rate by Company ──────────────────────────────────────
    if emails:
        st.subheader("Response Metrics")
        total_emailed = len(set(e.get("job_id") for e in emails))
        total_replied = sum(1 for a in applications if a.get("status") == "Recruiter Replied")
        reply_rate = (total_replied / total_emailed * 100) if total_emailed > 0 else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Jobs Emailed", total_emailed)
        with col2:
            st.metric("Reply Rate", f"{reply_rate:.1f}%")

        email_type_counts = Counter(e.get("email_type", "unknown") for e in emails)
        fig_email = px.bar(
            x=list(email_type_counts.keys()),
            y=list(email_type_counts.values()),
            labels={"x": "Email Type", "y": "Count"},
            title="Emails by Type",
        )
        st.plotly_chart(fig_email, use_container_width=True)

else:
    st.info("No application data yet. Start applying to see analytics!")

# ── Jobs by Source ───────────────────────────────────────────────────
if jobs:
    st.subheader("Jobs by Source")
    source_counts = Counter(j.get("source", "unknown") for j in jobs)
    fig_source = px.bar(
        x=list(source_counts.keys()),
        y=list(source_counts.values()),
        labels={"x": "Source", "y": "Jobs"},
        title="Discovered Jobs by Source",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig_source, use_container_width=True)

# ── Raw Data Tables ──────────────────────────────────────────────────
st.subheader("Raw Data")
tab1, tab2, tab3 = st.tabs(["Applications", "Emails", "Jobs"])
with tab1:
    if applications:
        st.dataframe(applications, use_container_width=True)
    else:
        st.info("No applications yet.")
with tab2:
    if emails:
        st.dataframe(emails, use_container_width=True)
    else:
        st.info("No emails sent yet.")
with tab3:
    if jobs:
        display_jobs = [{k: v for k, v in j.items() if k != "raw_json" and k != "jd_text"} for j in jobs]
        st.dataframe(display_jobs, use_container_width=True)
    else:
        st.info("No jobs discovered yet.")
