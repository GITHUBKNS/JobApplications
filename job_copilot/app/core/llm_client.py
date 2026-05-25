"""Unified LLM client abstracting Anthropic Claude and OpenAI GPT-4o."""
from __future__ import annotations

import json
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


class LLMClient:
    """Provider-agnostic LLM interface. Tries Claude first, falls back to OpenAI."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._anthropic = None
        self._openai = None

    def _get_anthropic(self):
        if self._anthropic is None:
            if not self._settings.anthropic_api_key:
                return None
            import anthropic
            self._anthropic = anthropic.Anthropic(api_key=self._settings.anthropic_api_key)
        return self._anthropic

    def _get_openai(self):
        if self._openai is None:
            if not self._settings.openai_api_key:
                return None
            import openai
            self._openai = openai.OpenAI(api_key=self._settings.openai_api_key)
        return self._openai

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def _call_claude(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        client = self._get_anthropic()
        if client is None:
            raise RuntimeError("Anthropic API key not configured")
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return resp.content[0].text

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def _call_openai(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        client = self._get_openai()
        if client is None:
            raise RuntimeError("OpenAI API key not configured")
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        return resp.choices[0].message.content

    def generate(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        prefer: str = "claude",
    ) -> str:
        """Generate text. Tries preferred provider first, then falls back."""
        providers = (
            [self._call_claude, self._call_openai]
            if prefer == "claude"
            else [self._call_openai, self._call_claude]
        )
        last_err: Optional[Exception] = None
        for call_fn in providers:
            try:
                return call_fn(system, user_message, max_tokens, temperature)
            except Exception as e:
                log.warning("llm_provider_failed", provider=call_fn.__name__, error=str(e))
                last_err = e
        raise RuntimeError(f"All LLM providers failed. Last error: {last_err}")

    def generate_json(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        prefer: str = "claude",
    ) -> Any:
        """Generate and parse JSON from LLM response."""
        system_with_json = system + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown fences, no commentary."
        raw = self.generate(system_with_json, user_message, max_tokens, temperature, prefer)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)
