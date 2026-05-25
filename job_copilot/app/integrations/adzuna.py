"""Adzuna job search integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import JobPosting

log = get_logger(__name__)

BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"


async def search_jobs(
    query: str = "Data Engineer",
    location: str = "New Jersey",
    posted_within_days: int = 7,
    page: int = 1,
) -> list[JobPosting]:
    settings = get_settings()
    if not settings.adzuna_app_id or not settings.adzuna_api_key:
        log.warning("adzuna_skipped", reason="ADZUNA credentials not set")
        return []

    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_api_key,
        "results_per_page": 50,
        "what": query,
        "where": location,
        "max_days_old": posted_within_days,
        "sort_by": "date",
        "content-type": "application/json",
    }

    jobs: list[JobPosting] = []
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(f"{BASE_URL}/{page}", params=params)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("results", []):
                jobs.append(_normalize(item))
            log.info("adzuna_results", count=len(jobs))
        except Exception as e:
            log.error("adzuna_error", error=str(e))
    return jobs


def _normalize(item: dict[str, Any]) -> JobPosting:
    posted_at = None
    if item.get("created"):
        try:
            posted_at = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    location_parts = []
    loc = item.get("location", {})
    for area in loc.get("area", []):
        location_parts.append(area)
    location_str = ", ".join(location_parts) if location_parts else ""

    salary = ""
    if item.get("salary_min") and item.get("salary_max"):
        salary = f"${item['salary_min']:,.0f} - ${item['salary_max']:,.0f}"

    return JobPosting(
        id=f"adzuna_{item.get('id', '')}",
        title=item.get("title", ""),
        company=item.get("company", {}).get("display_name", ""),
        location=location_str,
        remote="remote" in item.get("title", "").lower() or "remote" in item.get("description", "").lower(),
        posted_at=posted_at,
        source="adzuna",
        url=item.get("redirect_url", ""),
        jd_text=item.get("description", ""),
        salary=salary,
        company_domain="",
        raw_data=item,
    )
