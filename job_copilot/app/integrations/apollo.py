"""Apollo.io email finding integration (secondary)."""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import RecruiterCandidate

log = get_logger(__name__)

BASE_URL = "https://api.apollo.io/v1"


async def search_people(
    company_domain: str,
    titles: list[str] | None = None,
    limit: int = 5,
) -> list[RecruiterCandidate]:
    settings = get_settings()
    if not settings.apollo_api_key:
        log.warning("apollo_skipped", reason="APOLLO_API_KEY not set")
        return []

    if titles is None:
        titles = ["Recruiter", "Talent Acquisition", "HR", "Hiring Manager", "Engineering Manager"]

    payload = {
        "api_key": settings.apollo_api_key,
        "q_organization_domains": company_domain,
        "person_titles": titles,
        "page": 1,
        "per_page": limit,
    }

    candidates = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(f"{BASE_URL}/mixed_people/search", json=payload)
            resp.raise_for_status()
            data = resp.json()
            for person in data.get("people", []):
                candidates.append(RecruiterCandidate(
                    name=person.get("name", ""),
                    email=person.get("email", ""),
                    title=person.get("title", ""),
                    company=person.get("organization", {}).get("name", ""),
                    linkedin_url=person.get("linkedin_url", ""),
                    source="apollo",
                    confidence=0.7 if person.get("email") else 0.3,
                ))
            log.info("apollo_results", domain=company_domain, count=len(candidates))
        except Exception as e:
            log.error("apollo_error", error=str(e))
    return candidates
