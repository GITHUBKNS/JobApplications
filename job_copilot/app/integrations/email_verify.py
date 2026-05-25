"""Email verification via NeverBounce (primary) and ZeroBounce (fallback)."""
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


async def verify_email(email: str) -> tuple[bool, str]:
    """Verify email. Returns (is_valid, result_detail). Waterfall: NeverBounce → ZeroBounce."""
    valid, detail = await _verify_neverbounce(email)
    if detail != "skipped":
        return valid, detail
    return await _verify_zerobounce(email)


async def _verify_neverbounce(email: str) -> tuple[bool, str]:
    settings = get_settings()
    if not settings.neverbounce_api_key:
        return False, "skipped"

    params = {"key": settings.neverbounce_api_key, "email": email}
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://api.neverbounce.com/v4/single/check", params=params
            )
            resp.raise_for_status()
            data = resp.json()
            result = data.get("result", "unknown")
            is_valid = result in ("valid", "catchall")
            log.info("neverbounce_result", email=email, result=result)
            return is_valid, f"neverbounce:{result}"
        except Exception as e:
            log.error("neverbounce_error", error=str(e))
            return False, "skipped"


async def _verify_zerobounce(email: str) -> tuple[bool, str]:
    settings = get_settings()
    if not settings.zerobounce_api_key:
        return False, "skipped"

    params = {"api_key": settings.zerobounce_api_key, "email": email}
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://api.zerobounce.net/v2/validate", params=params
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "unknown")
            is_valid = status in ("valid", "catch-all")
            log.info("zerobounce_result", email=email, status=status)
            return is_valid, f"zerobounce:{status}"
        except Exception as e:
            log.error("zerobounce_error", error=str(e))
            return False, f"zerobounce:error:{e}"
