"""PDF rendering for resume and cover letter using Jinja2 + WeasyPrint."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.core.config import PROJECT_ROOT
from app.core.logging import get_logger
from app.models.schemas import MasterResume

log = get_logger(__name__)

TEMPLATES_DIR = PROJECT_ROOT / "app" / "templates"


def _get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )


def render_resume_pdf(resume: MasterResume, output_path: str | Path) -> Path:
    from weasyprint import HTML

    env = _get_jinja_env()
    template = env.get_template("resume/template.html")
    html_content = template.render(resume=resume)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_content).write_pdf(str(output_path))
    log.info("resume_pdf_rendered", path=str(output_path))
    return output_path


def render_cover_letter_pdf(
    text: str,
    candidate_name: str,
    company: str,
    job_title: str,
    output_path: str | Path,
) -> Path:
    from weasyprint import HTML

    env = _get_jinja_env()
    template = env.get_template("cover_letter/template.html")
    html_content = template.render(
        text=text,
        candidate_name=candidate_name,
        company=company,
        job_title=job_title,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_content).write_pdf(str(output_path))
    log.info("cover_letter_pdf_rendered", path=str(output_path))
    return output_path
