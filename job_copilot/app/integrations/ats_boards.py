"""Direct ATS board scraping for Greenhouse, Lever, Ashby, Workable, SmartRecruiters."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from app.core.logging import get_logger
from app.models.schemas import JobPosting

log = get_logger(__name__)


async def search_greenhouse(
    company_slug: str,
    keyword: str = "data engineer",
) -> list[JobPosting]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    return await _fetch_ats("greenhouse", url, company_slug, keyword, _parse_greenhouse)


async def search_lever(
    company_slug: str,
    keyword: str = "data engineer",
) -> list[JobPosting]:
    url = f"https://api.lever.co/v0/postings/{company_slug}"
    return await _fetch_ats("lever", url, company_slug, keyword, _parse_lever)


async def search_ashby(
    company_slug: str,
    keyword: str = "data engineer",
) -> list[JobPosting]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{company_slug}"
    return await _fetch_ats("ashby", url, company_slug, keyword, _parse_ashby)


async def search_workable(
    company_slug: str,
    keyword: str = "data engineer",
) -> list[JobPosting]:
    url = f"https://apply.workable.com/api/v3/accounts/{company_slug}/jobs"
    return await _fetch_ats_post("workable", url, company_slug, keyword, _parse_workable)


async def search_smartrecruiters(
    company_slug: str,
    keyword: str = "data engineer",
) -> list[JobPosting]:
    url = f"https://api.smartrecruiters.com/v1/companies/{company_slug}/postings"
    params = {"q": keyword, "limit": 100}
    return await _fetch_ats("smartrecruiters", url, company_slug, keyword, _parse_smartrecruiters, params=params)


async def _fetch_ats(
    source: str,
    url: str,
    company: str,
    keyword: str,
    parser,
    params: dict | None = None,
) -> list[JobPosting]:
    jobs = []
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            jobs = parser(data, company, keyword)
            log.info(f"{source}_results", company=company, count=len(jobs))
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                log.error(f"{source}_error", company=company, error=str(e))
        except Exception as e:
            log.error(f"{source}_error", company=company, error=str(e))
    return jobs


async def _fetch_ats_post(
    source: str,
    url: str,
    company: str,
    keyword: str,
    parser,
) -> list[JobPosting]:
    jobs = []
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.post(url, json={"query": keyword, "location": []})
            resp.raise_for_status()
            data = resp.json()
            jobs = parser(data, company, keyword)
            log.info(f"{source}_results", company=company, count=len(jobs))
        except Exception as e:
            log.error(f"{source}_error", company=company, error=str(e))
    return jobs


def _keyword_match(text: str, keyword: str) -> bool:
    kw_lower = keyword.lower()
    return any(part in text.lower() for part in kw_lower.split())


def _parse_greenhouse(data: dict, company: str, keyword: str) -> list[JobPosting]:
    results = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        if not _keyword_match(title, keyword):
            continue
        posted_at = None
        if job.get("updated_at"):
            try:
                posted_at = datetime.fromisoformat(job["updated_at"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        loc_name = ""
        if job.get("location", {}).get("name"):
            loc_name = job["location"]["name"]
        results.append(JobPosting(
            id=f"gh_{company}_{job['id']}",
            title=title,
            company=company,
            location=loc_name,
            remote="remote" in loc_name.lower(),
            posted_at=posted_at,
            source="greenhouse",
            url=job.get("absolute_url", ""),
            jd_text=job.get("content", ""),
            raw_data=job,
        ))
    return results


def _parse_lever(data: list | dict, company: str, keyword: str) -> list[JobPosting]:
    if isinstance(data, dict):
        data = data.get("postings", data.get("results", []))
    results = []
    for job in data:
        title = job.get("text", "")
        if not _keyword_match(title, keyword):
            continue
        posted_at = None
        if job.get("createdAt"):
            try:
                posted_at = datetime.fromtimestamp(job["createdAt"] / 1000)
            except (ValueError, TypeError, OSError):
                pass
        cats = job.get("categories", {})
        results.append(JobPosting(
            id=f"lever_{company}_{job.get('id', '')}",
            title=title,
            company=company,
            location=cats.get("location", ""),
            remote="remote" in cats.get("location", "").lower(),
            posted_at=posted_at,
            source="lever",
            url=job.get("hostedUrl", ""),
            jd_text=job.get("descriptionPlain", "") or job.get("description", ""),
            raw_data=job,
        ))
    return results


def _parse_ashby(data: dict, company: str, keyword: str) -> list[JobPosting]:
    results = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        if not _keyword_match(title, keyword):
            continue
        results.append(JobPosting(
            id=f"ashby_{company}_{job.get('id', '')}",
            title=title,
            company=company,
            location=job.get("location", ""),
            remote="remote" in job.get("location", "").lower(),
            source="ashby",
            url=job.get("jobUrl", ""),
            jd_text=job.get("descriptionPlain", "") or job.get("descriptionHtml", ""),
            raw_data=job,
        ))
    return results


def _parse_workable(data: dict, company: str, keyword: str) -> list[JobPosting]:
    results = []
    for job in data.get("results", []):
        title = job.get("title", "")
        if not _keyword_match(title, keyword):
            continue
        posted_at = None
        if job.get("published"):
            try:
                posted_at = datetime.fromisoformat(job["published"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        results.append(JobPosting(
            id=f"workable_{company}_{job.get('shortcode', job.get('id', ''))}",
            title=title,
            company=company,
            location=job.get("location", {}).get("location_str", ""),
            remote=job.get("remote", False),
            posted_at=posted_at,
            source="workable",
            url=job.get("url", f"https://apply.workable.com/{company}/j/{job.get('shortcode', '')}/"),
            jd_text=job.get("description", ""),
            raw_data=job,
        ))
    return results


def _parse_smartrecruiters(data: dict, company: str, keyword: str) -> list[JobPosting]:
    results = []
    for job in data.get("content", []):
        title = job.get("name", "")
        if not _keyword_match(title, keyword):
            continue
        posted_at = None
        if job.get("releasedDate"):
            try:
                posted_at = datetime.fromisoformat(job["releasedDate"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        loc = job.get("location", {})
        loc_str = loc.get("city", "") + ", " + loc.get("region", "")
        results.append(JobPosting(
            id=f"sr_{company}_{job.get('id', '')}",
            title=title,
            company=company,
            location=loc_str,
            remote=loc.get("remote", False),
            posted_at=posted_at,
            source="smartrecruiters",
            url=f"https://jobs.smartrecruiters.com/{company}/{job.get('id', '')}",
            jd_text=job.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text", ""),
            raw_data=job,
        ))
    return results
