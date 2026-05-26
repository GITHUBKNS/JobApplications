"""Visa sponsorship detection: regex + LLM classification on JD text."""
from __future__ import annotations

import re

from app.core.logging import get_logger

log = get_logger(__name__)

REJECT_PATTERNS = [
    r"(?i)\b(u\.?s\.?\s*citizen(s|ship)?(\s+only)?)\b",
    r"(?i)\b(must\s+be\s+(a\s+)?u\.?s\.?\s*citizen)\b",
    r"(?i)\b(permanent\s+resident(s)?\s+only)\b",
    r"(?i)\b(no\s+visa\s+sponsorship)\b",
    r"(?i)\b(not?\s+sponsor)\b",
    r"(?i)\b(unable\s+to\s+sponsor)\b",
    r"(?i)\b(will\s+not\s+sponsor)\b",
    r"(?i)\b(cannot\s+sponsor)\b",
    r"(?i)\b(do(es)?\s+not\s+offer\s+sponsor(ship)?)\b",
    r"(?i)\b(without\s+sponsorship)\b",
    r"(?i)\b(clearance\s+required)\b",
    r"(?i)\b(security\s+clearance)\b",
    r"(?i)\b(must\s+be\s+authorized\s+to\s+work\s+in\s+the\s+u\.?s\.?\s+without\s+sponsor(ship)?)\b",
    r"(?i)\b(not\s+eligible\s+for\s+visa\s+sponsorship)\b",
]

POSITIVE_PATTERNS = [
    r"(?i)\b(visa\s+sponsorship\s+(available|offered|provided|possible))\b",
    r"(?i)\b(will(ing)?\s+to\s+sponsor)\b",
    r"(?i)\b(h[- ]?1b\s+sponsor(ship)?)\b",
    r"(?i)\b(sponsor\s+h[- ]?1b)\b",
    r"(?i)\b(open\s+to\s+sponsor(ship|ing)?)\b",
    r"(?i)\b(sponsorship\s+(is\s+)?available)\b",
]


def classify_visa_signal(jd_text: str) -> str:
    """
    Returns:
      "reject" – JD explicitly excludes sponsored workers
      "positive" – JD indicates sponsorship available
      "unknown" – no clear signal
    """
    if not jd_text:
        return "unknown"

    for pattern in REJECT_PATTERNS:
        if re.search(pattern, jd_text):
            log.debug("visa_reject_pattern", pattern=pattern[:40])
            return "reject"

    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, jd_text):
            return "positive"

    return "unknown"


def should_filter_out(jd_text: str, require_sponsorship: bool = True) -> bool:
    """Return True if job should be filtered out based on visa requirements."""
    if not require_sponsorship:
        return False
    signal = classify_visa_signal(jd_text)
    return signal == "reject"
