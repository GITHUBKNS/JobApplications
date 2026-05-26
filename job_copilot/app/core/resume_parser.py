"""Parse uploaded PDF resume into structured MasterResume JSON via Claude."""
from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader

from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.models.schemas import MasterResume

log = get_logger(__name__)

PARSE_SYSTEM_PROMPT = """\
You are an expert resume parser. Extract structured data from the resume text below.
Return a JSON object with these exact keys:
{
  "contact": {"name","email","phone","location","linkedin","github","website"},
  "summary": "professional summary string",
  "skills": ["skill1","skill2",...],
  "experience": [{"company","title","location","start_date","end_date","bullets":["..."]}],
  "education": [{"institution","degree","field","start_date","end_date","gpa"}],
  "projects": [{"name","description","technologies":["..."],"url"}],
  "certifications": ["cert1","cert2"]
}
Be thorough. Parse every section. Use empty strings for missing fields, empty arrays for missing lists.
Dates should be in format like "Jan 2023" or "2023"."""


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def parse_resume_with_llm(pdf_path: str | Path) -> MasterResume:
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        raise ValueError("Could not extract text from PDF. The file may be image-based.")

    log.info("parsing_resume", chars=len(text))
    llm = LLMClient()
    data = llm.generate_json(
        system=PARSE_SYSTEM_PROMPT,
        user_message=f"Parse this resume:\n\n{text}",
        max_tokens=4096,
    )
    return MasterResume.model_validate(data)


def save_master_resume(resume: MasterResume, path: str | Path | None = None) -> Path:
    if path is None:
        from app.core.config import PROJECT_ROOT
        path = PROJECT_ROOT / "master_resume.json"
    path = Path(path)
    path.write_text(json.dumps(resume.model_dump(), indent=2, default=str))
    log.info("saved_master_resume", path=str(path))
    return path


def load_master_resume(path: str | Path | None = None) -> MasterResume | None:
    if path is None:
        from app.core.config import PROJECT_ROOT
        path = PROJECT_ROOT / "master_resume.json"
    path = Path(path)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return MasterResume.model_validate(data)
