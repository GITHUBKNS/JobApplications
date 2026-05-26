"""Tavily Search API for company news and personalization hooks."""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


async def search_company_news(
    company_name: str,
    max_results: int = 3,
) -> list[dict]:
    """Search for recent company news. Returns list of {title, url, content}."""
    settings = get_settings()
    if not settings.tavily_api_key:
        log.warning("tavily_skipped", reason="TAVILY_API_KEY not set")
        return []

    payload = {
        "api_key": settings.tavily_api_key,
        "query": f"{company_name} recent news hiring",
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.post("https://api.tavily.com/search", json=payload)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500],
                })
            log.info("tavily_results", company=company_name, count=len(results))
            return results
        except Exception as e:
            log.error("tavily_error", error=str(e))
            return []
