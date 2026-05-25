"""Orchestrate job discovery across all sources."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.dedup import deduplicate
from app.core.logging import get_logger
from app.core.visa_classifier import classify_visa_signal, should_filter_out
from app.db import sqlite_cache as cache
from app.integrations import adzuna, ats_boards, jsearch
from app.models.schemas import JobPosting

log = get_logger(__name__)

DEFAULT_ATS_COMPANIES = [
    "stripe", "datadog", "figma", "notion", "plaid", "reddit",
    "coinbase", "ramp", "brex", "dbt-labs", "databricks",
    "snowflake", "confluent", "elastic", "mongodb",
]


async def discover_jobs(
    keywords: list[str] | None = None,
    locations: list[str] | None = None,
    posted_within_days: int = 7,
    require_visa_sponsorship: bool = True,
    salary_floor: int | None = None,
    ats_companies: list[str] | None = None,
) -> list[JobPosting]:
    if keywords is None:
        keywords = ["Data Engineer", "Analytics Engineer"]
    if locations is None:
        locations = ["Newark, NJ", "Remote", "United States"]
    if ats_companies is None:
        ats_companies = DEFAULT_ATS_COMPANIES

    all_jobs: list[JobPosting] = []
    tasks = []

    for kw in keywords:
        for loc in locations:
            tasks.append(jsearch.search_jobs(query=kw, location=loc, posted_within_days=posted_within_days))
            tasks.append(adzuna.search_jobs(query=kw, location=loc, posted_within_days=posted_within_days))

    for company in ats_companies:
        for kw in keywords:
            tasks.append(ats_boards.search_greenhouse(company, kw))
            tasks.append(ats_boards.search_lever(company, kw))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            log.error("discovery_task_error", error=str(result))
            continue
        if isinstance(result, list):
            all_jobs.extend(result)

    log.info("discovery_raw_results", count=len(all_jobs))

    cutoff = datetime.utcnow() - timedelta(days=posted_within_days)
    filtered = []
    for job in all_jobs:
        if job.posted_at and job.posted_at.replace(tzinfo=None) < cutoff:
            continue
        if should_filter_out(job.jd_text, require_visa_sponsorship):
            continue
        job.visa_sponsorship_signal = classify_visa_signal(job.jd_text)
        filtered.append(job)

    unique = deduplicate(filtered)

    for job in unique:
        cache.upsert_job(job.model_dump(mode="json"))

    log.info("discovery_final", raw=len(all_jobs), filtered=len(filtered), unique=len(unique))
    return unique


def run_discovery_sync(**kwargs) -> list[JobPosting]:
    """Synchronous wrapper for Streamlit."""
    return asyncio.run(discover_jobs(**kwargs))
