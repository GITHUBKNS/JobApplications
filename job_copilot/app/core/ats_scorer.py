"""ATS scoring: JD-vs-resume gap analysis and resume tailoring."""
from __future__ import annotations

import json
from pathlib import Path

from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.models.schemas import ATSAnalysis, MasterResume

log = get_logger(__name__)

JD_ANALYSIS_PROMPT = """\
You are an expert ATS (Applicant Tracking System) analyst. Analyze the job description and extract:
1. hard_skills: specific technical skills required
2. tools: specific tools, frameworks, platforms mentioned
3. keywords: important keywords for ATS matching
4. yoe_signals: years of experience requirements mentioned
5. soft_skills: soft skills mentioned

Return JSON:
{
  "hard_skills": ["skill1", ...],
  "tools": ["tool1", ...],
  "keywords": ["keyword1", ...],
  "yoe_signals": ["3+ years Python", ...],
  "soft_skills": ["communication", ...]
}"""

ATS_SCORE_PROMPT = """\
You are an ATS scoring expert. Compare the resume against the job requirements and produce:
1. score: 0-100 ATS compatibility score
2. matched_keywords: keywords found in both resume and JD
3. missing_keywords: important JD keywords NOT in resume
4. suggestions: specific, actionable bullet-rewrite suggestions to improve ATS score

Return JSON:
{
  "score": 75,
  "matched_keywords": [...],
  "missing_keywords": [...],
  "suggestions": ["Rewrite bullet X to include keyword Y", ...]
}"""

TAILOR_PROMPT = """\
You are an expert resume writer optimizing for ATS systems.
Given the master resume and a target job description, rewrite ONLY the experience bullets
to better match the job requirements.

HARD RULES:
- Only rephrase or re-emphasize existing experience. Never invent employers, dates, or skills not in the master resume.
- Surface relevant keywords naturally in bullet points.
- Keep bullets concise and impact-focused (action verb + result + metric where possible).
- Maintain truthfulness — never fabricate experience.

Return a JSON object with the same structure as the input resume, with modified experience bullets.
All other fields (contact, education, projects, etc.) should remain unchanged."""


def analyze_jd(jd_text: str) -> dict:
    llm = LLMClient()
    return llm.generate_json(
        system=JD_ANALYSIS_PROMPT,
        user_message=f"Analyze this job description:\n\n{jd_text}",
    )


def score_resume(resume: MasterResume, jd_text: str) -> ATSAnalysis:
    jd_analysis = analyze_jd(jd_text)

    llm = LLMClient()
    resume_text = json.dumps(resume.model_dump(), indent=2)

    scoring_input = f"""JD Analysis:
{json.dumps(jd_analysis, indent=2)}

Resume:
{resume_text}"""

    result = llm.generate_json(
        system=ATS_SCORE_PROMPT,
        user_message=scoring_input,
    )

    return ATSAnalysis(
        score=result.get("score", 0),
        matched_keywords=result.get("matched_keywords", []),
        missing_keywords=result.get("missing_keywords", []),
        suggestions=result.get("suggestions", []),
        jd_skills=jd_analysis.get("hard_skills", []),
        jd_tools=jd_analysis.get("tools", []),
        jd_yoe_signals=jd_analysis.get("yoe_signals", []),
    )


def tailor_resume(resume: MasterResume, jd_text: str) -> MasterResume:
    llm = LLMClient()
    resume_text = json.dumps(resume.model_dump(), indent=2)

    result = llm.generate_json(
        system=TAILOR_PROMPT,
        user_message=f"Master Resume:\n{resume_text}\n\nTarget Job Description:\n{jd_text}",
        max_tokens=8192,
    )

    return MasterResume.model_validate(result)


def save_tailored_resume(resume: MasterResume, company: str, job_id: str) -> Path:
    from app.core.config import PROJECT_ROOT
    output_dir = PROJECT_ROOT / "output" / f"{company}_{job_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "tailored_resume.json"
    path.write_text(json.dumps(resume.model_dump(), indent=2, default=str))
    return path
