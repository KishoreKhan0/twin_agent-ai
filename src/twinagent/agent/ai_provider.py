"""LLM provider abstraction for TwinAgent AI.

The copilot can run in two modes:

1. Deterministic fallback mode: no API key needed.
2. OpenAI mode: enabled only when TWINAGENT_AI_ENABLED=1 and OPENAI_API_KEY exists.

This keeps the project runnable for reviewers while allowing real AI reasoning
when credentials are available.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Protocol

from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass(frozen=True)
class LLMResponse:
    """A generated LLM response."""

    text: str
    provider: str
    model: str
    used_ai: bool


class LLMProvider(Protocol):
    """Interface for AI providers."""

    def is_available(self) -> bool:
        """Return whether the provider can generate real AI answers."""

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Generate an answer."""


@dataclass(frozen=True)
class DeterministicFallbackProvider:
    """Provider used when no real AI provider is enabled."""

    reason: str = "OpenAI provider not enabled or API key missing."

    def is_available(self) -> bool:
        """Return False because this provider is a fallback."""
        return False

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a fallback response."""
        return LLMResponse(
            text=self.reason,
            provider="deterministic_fallback",
            model="none",
            used_ai=False,
        )


@dataclass(frozen=True)
class OpenAIProvider:
    """OpenAI SDK-backed LLM provider."""

    model: str
    temperature: float = 0.1

    def is_available(self) -> bool:
        """Return True only when AI mode and an API key are configured."""
        enabled = os.getenv("TWINAGENT_AI_ENABLED", "0").strip().lower()
        return enabled in {"1", "true", "yes", "on"} and bool(os.getenv("OPENAI_API_KEY"))

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Generate an answer using the OpenAI Python SDK."""
        if not self.is_available():
            return LLMResponse(
                text="OpenAI provider is not enabled.",
                provider="openai",
                model=self.model,
                used_ai=False,
            )

        try:
            from openai import OpenAI
        except ImportError as error:
            raise ImportError(
                "openai package is required for AI copilot mode. "
                "Install dependencies with: pip install -r requirements.txt"
            ) from error

        client = OpenAI()

        # Chat Completions remains simple and stable for this project. The rest of
        # the system handles tool/context selection before the model is called.
        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        return LLMResponse(
            text=text.strip(),
            provider="openai",
            model=self.model,
            used_ai=True,
        )


def create_llm_provider() -> LLMProvider:
    """Create the configured LLM provider."""
    model = os.getenv("TWINAGENT_LLM_MODEL", "gpt-4o-mini")
    temperature_text = os.getenv("TWINAGENT_LLM_TEMPERATURE", "0.1")

    try:
        temperature = float(temperature_text)
    except ValueError:
        temperature = 0.1

    provider = OpenAIProvider(model=model, temperature=temperature)
    if provider.is_available():
        return provider

    return DeterministicFallbackProvider()
