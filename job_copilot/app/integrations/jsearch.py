"""JSearch (RapidAPI) job search integration."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import JobPosting

log = get_logger(__name__)

BASE_URL = "https://jsearch.p.rapidapi.com/search"


async def search_jobs(
    query: str = "Data Engineer",
    location: str = "United States",
    posted_within_days: int = 7,
    page: int = 1,
    num_pages: int = 3,
) -> list[JobPosting]:
    settings = get_settings()
    if not settings.jsearch_api_key:
        log.warning("jsearch_skipped", reason="JSEARCH_API_KEY not set")
        return []

    headers = {
        "X-RapidAPI-Key": settings.jsearch_api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    date_posted = "week" if posted_within_days <= 7 else "month"
    params = {
        "query": f"{query} in {location}",
        "page": str(page),
        "num_pages": str(num_pages),
        "date_posted": date_posted,
        "remote_jobs_only": "false",
    }

    jobs: list[JobPosting] = []
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(BASE_URL, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("data", []):
                jobs.append(_normalize(item))
            log.info("jsearch_results", count=len(jobs))
        except Exception as e:
            log.error("jsearch_error", error=str(e))
    return jobs


def _normalize(item: dict[str, Any]) -> JobPosting:
    posted_at = None
    if item.get("job_posted_at_datetime_utc"):
        try:
            posted_at = datetime.fromisoformat(
                item["job_posted_at_datetime_utc"].replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            pass

    return JobPosting(
        id=f"jsearch_{item.get('job_id', '')}",
        title=item.get("job_title", ""),
        company=item.get("employer_name", ""),
        location=item.get("job_city", "") + ", " + item.get("job_state", ""),
        remote=item.get("job_is_remote", False),
        posted_at=posted_at,
        source="jsearch",
        url=item.get("job_apply_link", "") or item.get("job_google_link", ""),
        jd_text=item.get("job_description", ""),
        salary=_extract_salary(item),
        company_domain=item.get("employer_website", ""),
        raw_data=item,
    )


def _extract_salary(item: dict) -> str:
    min_sal = item.get("job_min_salary")
    max_sal = item.get("job_max_salary")
    if min_sal and max_sal:
        return f"${min_sal:,.0f} - ${max_sal:,.0f}"
    if min_sal:
        return f"${min_sal:,.0f}+"
    return ""
