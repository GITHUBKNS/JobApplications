"""Settings page: upload resume, parse, edit, configure Google Sheets."""
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.config import PROJECT_ROOT, get_settings
from app.core.logging import get_logger, setup_logging
from app.core.resume_parser import (
    extract_text_from_pdf,
    load_master_resume,
    parse_resume_with_llm,
    save_master_resume,
)
from app.models.schemas import MasterResume

setup_logging()
log = get_logger(__name__)
settings = get_settings()

st.title("Settings")

# ── API Key Status ──────────────────────────────────────────────────────
st.header("API Key Status")
api_keys = {
    "Anthropic (Claude)": settings.anthropic_api_key,
    "OpenAI (GPT-4o)": settings.openai_api_key,
    "JSearch (RapidAPI)": settings.jsearch_api_key,
    "Adzuna": settings.adzuna_api_key,
    "Hunter.io": settings.hunter_api_key,
    "Apollo.io": settings.apollo_api_key,
    "RocketReach": settings.rocketreach_api_key,
    "NeverBounce": settings.neverbounce_api_key,
    "ZeroBounce": settings.zerobounce_api_key,
    "Tavily": settings.tavily_api_key,
    "Google Service Account": str(settings.service_account_path.exists()) if settings.google_service_account_file else "",
    "Gmail OAuth": settings.gmail_oauth_client_id,
    "LinkedIn Cookie": settings.linkedin_session_cookie,
}

cols = st.columns(3)
for i, (name, val) in enumerate(api_keys.items()):
    with cols[i % 3]:
        if val and val not in ("False",):
            st.success(f"{name}: Configured")
        else:
            st.warning(f"{name}: Not set")

# ── Resume Upload & Parsing ────────────────────────────────────────────
st.header("Master Resume")

resume = load_master_resume()

uploaded = st.file_uploader("Upload your master resume (PDF)", type=["pdf"])
if uploaded is not None:
    pdf_path = PROJECT_ROOT / "master_resume.pdf"
    pdf_path.write_bytes(uploaded.getvalue())
    st.success(f"Saved PDF to {pdf_path.name}")

    if st.button("Parse Resume with AI"):
        with st.spinner("Parsing resume via Claude/GPT-4o..."):
            try:
                resume = parse_resume_with_llm(pdf_path)
                save_master_resume(resume)
                st.success("Resume parsed and saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing resume: {e}")

if resume:
    st.subheader("Parsed Resume Preview")

    with st.expander("Contact Info", expanded=True):
        c = resume.contact
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=c.name, key="contact_name")
            email = st.text_input("Email", value=c.email, key="contact_email")
            phone = st.text_input("Phone", value=c.phone, key="contact_phone")
        with col2:
            location = st.text_input("Location", value=c.location, key="contact_location")
            linkedin = st.text_input("LinkedIn", value=c.linkedin, key="contact_linkedin")
            github = st.text_input("GitHub", value=c.github, key="contact_github")

    with st.expander("Summary"):
        summary = st.text_area("Professional Summary", value=resume.summary, height=100, key="summary")

    with st.expander("Skills"):
        skills_text = st.text_area(
            "Skills (one per line)",
            value="\n".join(resume.skills),
            height=150,
            key="skills",
        )

    with st.expander("Experience"):
        for i, exp in enumerate(resume.experience):
            st.markdown(f"**{exp.title}** at {exp.company}")
            st.caption(f"{exp.start_date} – {exp.end_date} | {exp.location}")
            for bullet in exp.bullets:
                st.markdown(f"- {bullet}")
            st.markdown("---")

    with st.expander("Education"):
        for edu in resume.education:
            st.markdown(f"**{edu.degree}** {'in ' + edu.field if edu.field else ''}")
            st.markdown(f"{edu.institution} | {edu.start_date} – {edu.end_date}")

    with st.expander("Projects"):
        for proj in resume.projects:
            st.markdown(f"**{proj.name}**: {proj.description}")
            if proj.technologies:
                st.caption(", ".join(proj.technologies))

    if st.button("Save Changes"):
        resume.contact.name = name
        resume.contact.email = email
        resume.contact.phone = phone
        resume.contact.location = location
        resume.contact.linkedin = linkedin
        resume.contact.github = github
        resume.summary = summary
        resume.skills = [s.strip() for s in skills_text.split("\n") if s.strip()]
        save_master_resume(resume)
        st.success("Resume saved!")

    st.subheader("Raw JSON")
    st.json(resume.model_dump())
else:
    st.info("Upload a PDF resume above to get started.")

# ── Google Sheets Bootstrap ─────────────────────────────────────────────
st.header("Google Sheets")

if settings.service_account_path.exists():
    if st.button("Initialize / Connect Google Sheets"):
        with st.spinner("Connecting to Google Sheets..."):
            try:
                from app.db.sheets import SheetsClient
                client = SheetsClient()
                ss = client.get_or_create_spreadsheet()
                st.success(f"Spreadsheet ready!")
                st.markdown(f"[Open Spreadsheet]({client.url})")
                st.code(client.url)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning(
        f"Google service account file not found at `{settings.service_account_path}`. "
        "Add your service account JSON to connect to Google Sheets."
    )

# ── User Profile Defaults ──────────────────────────────────────────────
st.header("Profile Defaults")
st.info("These defaults are loaded from .env. Edit .env to change them.")
st.markdown(f"""
- **Name:** {settings.user_name}
- **Location:** {settings.user_location}
- **Daily Email Cap:** {settings.daily_email_cap}
- **Max Email Cap:** {settings.max_email_cap}
""")
