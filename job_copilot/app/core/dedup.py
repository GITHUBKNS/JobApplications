"""Deduplicate job postings across sources via fuzzy matching."""
from __future__ import annotations

import re

from rapidfuzz import fuzz

from app.core.logging import get_logger
from app.models.schemas import JobPosting

log = get_logger(__name__)

SIMILARITY_THRESHOLD = 85


def normalize_company(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"\s*(inc\.?|llc|ltd\.?|corp\.?|co\.?|,?\s*inc)\s*$", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    return name.strip()


def normalize_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"\s*[\(\[].*?[\)\]]", "", title)
    title = re.sub(r"\s*[-–—].*$", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def are_duplicates(a: JobPosting, b: JobPosting) -> bool:
    company_sim = fuzz.ratio(normalize_company(a.company), normalize_company(b.company))
    if company_sim < 70:
        return False
    title_sim = fuzz.ratio(normalize_title(a.title), normalize_title(b.title))
    return title_sim >= SIMILARITY_THRESHOLD


def deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:
    """Remove duplicate jobs, keeping the first occurrence (by source priority)."""
    if not jobs:
        return []

    unique: list[JobPosting] = []
    for job in jobs:
        is_dup = False
        for existing in unique:
            if are_duplicates(job, existing):
                is_dup = True
                break
        if not is_dup:
            unique.append(job)

    removed = len(jobs) - len(unique)
    if removed > 0:
        log.info("dedup_complete", original=len(jobs), unique=len(unique), removed=removed)
    return unique
