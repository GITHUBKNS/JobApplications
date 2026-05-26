"""Generate autofill payload for job applications."""
from __future__ import annotations

import json

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import AutofillPayload, MasterResume

log = get_logger(__name__)


def generate_autofill(resume: MasterResume) -> AutofillPayload:
    settings = get_settings()

    years_exp: dict[str, int] = {}
    for skill in resume.skills[:20]:
        years_exp[skill] = 3

    return AutofillPayload(
        full_name=resume.contact.name or settings.user_name,
        email=resume.contact.email or settings.user_email,
        phone=resume.contact.phone or settings.user_phone,
        linkedin=resume.contact.linkedin,
        website=resume.contact.website or resume.contact.github,
        years_experience=years_exp,
        work_authorization="Require sponsorship",
        sponsorship_needed="Yes",
        willing_to_relocate="Yes",
        salary_expectation="",
        start_date="2 weeks notice",
    )


def format_autofill_clipboard(payload: AutofillPayload) -> str:
    """Format payload as clipboard-friendly text."""
    lines = [
        f"Full Name: {payload.full_name}",
        f"Email: {payload.email}",
        f"Phone: {payload.phone}",
        f"LinkedIn: {payload.linkedin}",
        f"Website: {payload.website}",
        "",
        "Work Authorization: Require sponsorship",
        "Sponsorship Needed: Yes",
        f"Willing to Relocate: {payload.willing_to_relocate}",
        f"Salary Expectation: {payload.salary_expectation or 'Negotiable'}",
        f"Start Date: {payload.start_date}",
        "",
        "Years of Experience by Skill:",
    ]
    for skill, years in payload.years_experience.items():
        lines.append(f"  {skill}: {years} years")
    return "\n".join(lines)
