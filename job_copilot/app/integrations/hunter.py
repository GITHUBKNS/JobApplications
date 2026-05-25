"""Hunter.io email finding integration."""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import RecruiterCandidate

log = get_logger(__name__)

BASE_URL = "https://api.hunter.io/v2"


async def domain_search(
    domain: str,
    title_filter: str = "recruiter,talent,HR,hiring,engineering manager",
    limit: int = 10,
) -> list[RecruiterCandidate]:
    settings = get_settings()
    if not settings.hunter_api_key:
        log.warning("hunter_skipped", reason="HUNTER_API_KEY not set")
        return []

    params = {
        "domain": domain,
        "api_key": settings.hunter_api_key,
        "limit": limit,
    }

    candidates = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(f"{BASE_URL}/domain-search", params=params)
            resp.raise_for_status()
            data = resp.json()
            for email_obj in data.get("data", {}).get("emails", []):
                position = (email_obj.get("position") or "").lower()
                title_keywords = [t.strip().lower() for t in title_filter.split(",")]
                if not any(kw in position for kw in title_keywords):
                    continue
                candidates.append(RecruiterCandidate(
                    name=f"{email_obj.get('first_name', '')} {email_obj.get('last_name', '')}".strip(),
                    email=email_obj.get("value", ""),
                    title=email_obj.get("position", ""),
                    company=email_obj.get("company", ""),
                    source="hunter",
                    confidence=email_obj.get("confidence", 0) / 100.0,
                ))
            log.info("hunter_results", domain=domain, count=len(candidates))
        except Exception as e:
            log.error("hunter_error", error=str(e))
    return candidates


async def email_finder(domain: str, first_name: str, last_name: str) -> str | None:
    settings = get_settings()
    if not settings.hunter_api_key:
        return None

    params = {
        "domain": domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": settings.hunter_api_key,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(f"{BASE_URL}/email-finder", params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("email")
        except Exception as e:
            log.error("hunter_finder_error", error=str(e))
            return None
