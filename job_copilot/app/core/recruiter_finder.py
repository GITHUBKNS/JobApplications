"""Recruiter discovery: parse JD, LinkedIn search, email finding waterfall."""
from __future__ import annotations

import asyncio
import re

from app.core.logging import get_logger
from app.integrations import apollo, email_verify, hunter, rocketreach
from app.models.schemas import RecruiterCandidate

log = get_logger(__name__)


def extract_recruiter_from_jd(jd_text: str) -> list[RecruiterCandidate]:
    """Try to find explicit recruiter name/email in JD text."""
    candidates = []
    email_pattern = r'[\w.+-]+@[\w-]+\.[\w.-]+'
    emails = re.findall(email_pattern, jd_text)

    for email in emails:
        if any(skip in email.lower() for skip in ["noreply", "no-reply", "careers@", "jobs@", "apply@"]):
            continue
        candidates.append(RecruiterCandidate(
            name="",
            email=email,
            source="jd_parse",
            confidence=0.9,
        ))
    return candidates


async def find_recruiters(
    company: str,
    company_domain: str,
    jd_text: str = "",
    team: str = "",
) -> list[RecruiterCandidate]:
    """Waterfall recruiter finding: JD parse → Hunter → Apollo → RocketReach."""
    all_candidates: list[RecruiterCandidate] = []

    jd_candidates = extract_recruiter_from_jd(jd_text)
    all_candidates.extend(jd_candidates)

    if company_domain:
        hunter_results = await hunter.domain_search(company_domain)
        all_candidates.extend(hunter_results)

    if company_domain:
        apollo_results = await apollo.search_people(company_domain)
        all_candidates.extend(apollo_results)

    rr_results = await rocketreach.search_people(company)
    all_candidates.extend(rr_results)

    seen_emails: set[str] = set()
    unique: list[RecruiterCandidate] = []
    for c in all_candidates:
        if c.email and c.email.lower() not in seen_emails:
            seen_emails.add(c.email.lower())
            unique.append(c)
        elif not c.email:
            unique.append(c)

    unique.sort(key=lambda c: c.confidence, reverse=True)

    log.info("recruiter_search_complete", company=company, candidates=len(unique))
    return unique[:10]


async def verify_recruiter_email(candidate: RecruiterCandidate) -> RecruiterCandidate:
    """Verify a recruiter's email address."""
    if not candidate.email:
        return candidate

    is_valid, detail = await email_verify.verify_email(candidate.email)
    candidate.verified = is_valid
    candidate.verification_result = detail
    return candidate
