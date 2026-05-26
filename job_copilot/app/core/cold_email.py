"""Cold email generation and sending with follow-up cadence."""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.models.schemas import MasterResume

log = get_logger(__name__)

COLD_EMAIL_PROMPT = """\
You are an expert cold email copywriter for job applications. Write a cold outreach email
to a recruiter or hiring manager about a specific role.

Requirements:
- Subject line: create 2 A/B variants, short and compelling (no generic "Interested in..." subjects)
- Body: under 120 words total
- Include ONE specific personalization hook (from the provided context)
- Soft CTA (e.g., "Would love to learn more about the role — happy to chat whenever works for you")
- Professional but human tone — not stiff, not overly casual
- Do NOT include attachments inline — mention resume link in signature or offer to share
- Do NOT use phrases like "I came across your profile" or "I hope this finds you well"

Return JSON:
{
  "subject_a": "first subject line variant",
  "subject_b": "second subject line variant",
  "body": "email body text (plain text, use \\n for paragraphs)"
}"""

FOLLOWUP_PROMPT = """\
Write a brief follow-up email for a job application cold outreach.
This is follow-up #{followup_number} (sent {days} days after the original email).

Requirements:
- Under 60 words
- Reference the original email briefly
- Add one new piece of value or restate interest
- Soft CTA
- Do NOT be pushy or apologetic

Return JSON:
{
  "subject": "Re: {original_subject}",
  "body": "follow-up body text"
}"""


def generate_cold_email(
    resume: MasterResume,
    jd_text: str,
    company: str,
    job_title: str,
    recruiter_name: str = "",
    recruiter_linkedin_activity: str = "",
    company_news: str = "",
) -> dict:
    llm = LLMClient()

    personalization = ""
    if recruiter_linkedin_activity:
        personalization += f"Recruiter's recent LinkedIn activity: {recruiter_linkedin_activity}\n"
    if company_news:
        personalization += f"Recent company news: {company_news}\n"

    user_msg = f"""Generate a cold email for:

Company: {company}
Role: {job_title}
Recruiter Name: {recruiter_name or "Hiring Team"}
Candidate Name: {resume.contact.name}

Personalization Context:
{personalization or "No specific personalization available — use role and company details."}

Job Description (excerpt):
{jd_text[:2000]}

Candidate Background (brief):
Skills: {', '.join(resume.skills[:15])}
Recent Role: {resume.experience[0].title + ' at ' + resume.experience[0].company if resume.experience else 'N/A'}"""

    return llm.generate_json(
        system=COLD_EMAIL_PROMPT,
        user_message=user_msg,
        temperature=0.6,
    )


def generate_followup(
    original_subject: str,
    company: str,
    job_title: str,
    followup_number: int = 1,
    candidate_name: str = "",
) -> dict:
    llm = LLMClient()
    days = 3 if followup_number == 1 else 7

    prompt = FOLLOWUP_PROMPT.replace("{followup_number}", str(followup_number)).replace("{days}", str(days))

    user_msg = f"""Original subject: {original_subject}
Company: {company}
Role: {job_title}
Candidate: {candidate_name}
Original email subject to reply to: {original_subject}"""

    return llm.generate_json(
        system=prompt,
        user_message=user_msg,
        temperature=0.5,
    )


def get_send_time_within_business_hours() -> datetime:
    """Get a randomized send time within business hours (9 AM - 5 PM ET)."""
    now = datetime.utcnow()
    et_offset = timedelta(hours=-4)
    et_now = now + et_offset

    if et_now.hour < 9:
        delay_minutes = random.randint(0, 60)
        send_time = et_now.replace(hour=9, minute=delay_minutes, second=0)
    elif et_now.hour >= 17:
        send_time = et_now + timedelta(days=1)
        send_time = send_time.replace(hour=9, minute=random.randint(0, 60), second=0)
    else:
        delay_minutes = random.randint(5, 45)
        send_time = et_now + timedelta(minutes=delay_minutes)

    return send_time - et_offset
