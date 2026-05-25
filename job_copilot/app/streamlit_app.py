"""Main Streamlit application entry point."""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Job Application Copilot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()

st.sidebar.title("Job Copilot")
st.sidebar.markdown("---")

missing = []
if not settings.anthropic_api_key and not settings.openai_api_key:
    missing.append("LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)")

if missing:
    st.sidebar.warning("Missing configs:\n" + "\n".join(f"• {m}" for m in missing))

pages = {
    "Settings": "pages/1_Settings.py",
    "Search Jobs": "pages/2_Search_Jobs.py",
    "Resume Tailoring": "pages/3_Resume_Tailoring.py",
    "Cover Letter": "pages/4_Cover_Letter.py",
    "Apply": "pages/5_Apply.py",
    "Find Recruiter": "pages/6_Find_Recruiter.py",
    "Cold Email": "pages/7_Cold_Email.py",
    "Analytics": "pages/8_Analytics.py",
}

st.sidebar.markdown("### Navigation")
for name in pages:
    st.sidebar.page_link(f"pages/{list(pages.keys()).index(name) + 1}_{name.replace(' ', '_')}.py", label=name)

st.title("Job Application Copilot")
st.markdown("""
Welcome to your personal job application copilot. This tool helps you:

1. **Discover** fresh Data Engineer jobs across multiple portals
2. **Tailor** your resume and generate cover letters per job
3. **Find** and verify recruiter email addresses
4. **Send** personalized cold emails with follow-up cadence
5. **Track** everything in Google Sheets with analytics

Use the sidebar to navigate between pages.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Profile", settings.user_name)
with col2:
    st.metric("Location", settings.user_location)
with col3:
    st.metric("Daily Email Cap", settings.daily_email_cap)
