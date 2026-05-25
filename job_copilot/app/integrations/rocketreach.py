"""RocketReach email finding integration (tertiary)."""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import RecruiterCandidate

log = get_logger(__name__)

BASE_URL = "https://api.rocketreach.co/api/v2"


async def search_people(
    company_name: str,
    titles: list[str] | None = None,
    limit: int = 5,
) -> list[RecruiterCandidate]:
    settings = get_settings()
    if not settings.rocketreach_api_key:
        log.warning("rocketreach_skipped", reason="ROCKETREACH_API_KEY not set")
        return []

    if titles is None:
        titles = ["Recruiter", "Talent Acquisition", "HR Manager"]

    headers = {"Api-Key": settings.rocketreach_api_key}
    payload = {
        "current_employer": [company_name],
        "current_title": titles,
        "page_size": limit,
    }

    candidates = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post(
                f"{BASE_URL}/lookupProfile",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            for profile in data.get("profiles", []):
                email = ""
                for e in profile.get("emails", []):
                    if e.get("smtp_valid") == "valid":
                        email = e.get("email", "")
                        break
                if not email and profile.get("emails"):
                    email = profile["emails"][0].get("email", "")
                candidates.append(RecruiterCandidate(
                    name=profile.get("name", ""),
                    email=email,
                    title=profile.get("current_title", ""),
                    company=profile.get("current_employer", ""),
                    linkedin_url=profile.get("linkedin_url", ""),
                    source="rocketreach",
                    confidence=0.6 if email else 0.2,
                ))
            log.info("rocketreach_results", company=company_name, count=len(candidates))
        except Exception as e:
            log.error("rocketreach_error", error=str(e))
    return candidates
