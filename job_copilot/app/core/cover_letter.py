"""Cover letter generation via LLM."""
from __future__ import annotations

import json
from pathlib import Path

from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.models.schemas import MasterResume

log = get_logger(__name__)

COVER_LETTER_PROMPT = """\
You are an expert career coach writing a cover letter for a job application.

Requirements:
- Professional, concise tone
- Exactly 3 short paragraphs, approximately 250 words total
- Paragraph 1: Hook — mention the specific role and one reason you're excited about the company
- Paragraph 2: Value — connect 2-3 specific experiences/skills from the resume to the JD requirements
- Paragraph 3: Close — express enthusiasm, mention availability, soft CTA for next steps
- If a personalization hook (company news) is provided, weave it into paragraph 1 naturally
- Do NOT use clichés like "I am writing to express my interest" or "I believe I am a perfect fit"
- Address to "Hiring Team" unless a specific name is provided
- Sign off with the candidate's name

Return ONLY the cover letter text, no JSON, no markdown formatting."""


def generate_cover_letter(
    resume: MasterResume,
    jd_text: str,
    company: str,
    job_title: str,
    company_news: str = "",
    recruiter_name: str = "",
) -> str:
    llm = LLMClient()

    user_msg = f"""Generate a cover letter for:

Company: {company}
Role: {job_title}
{"Addressed to: " + recruiter_name if recruiter_name else ""}
{"Company News / Personalization Hook: " + company_news if company_news else ""}

Job Description:
{jd_text[:3000]}

Candidate Resume:
{json.dumps(resume.model_dump(), indent=2)[:3000]}"""

    return llm.generate(
        system=COVER_LETTER_PROMPT,
        user_message=user_msg,
        max_tokens=1500,
        temperature=0.5,
    )


def save_cover_letter(text: str, company: str, job_id: str) -> Path:
    from app.core.config import PROJECT_ROOT
    output_dir = PROJECT_ROOT / "output" / f"{company}_{job_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "cover_letter.txt"
    path.write_text(text)
    return path
