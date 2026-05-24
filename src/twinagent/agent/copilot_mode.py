"""Copilot execution-mode helpers for TwinAgent AI."""

from __future__ import annotations

from enum import Enum


class CopilotMode(str, Enum):
    """Supported copilot execution modes."""

    DETERMINISTIC = "deterministic"
    AI = "ai"
    AUTO = "auto"


def normalize_copilot_mode(value: str | None) -> CopilotMode:
    """Normalize user/API mode input into a supported mode."""
    if value is None:
        return CopilotMode.AUTO

    normalized = str(value).strip().lower().replace("_", "-")

    aliases = {
        "deterministic": CopilotMode.DETERMINISTIC,
        "rules": CopilotMode.DETERMINISTIC,
        "rule": CopilotMode.DETERMINISTIC,
        "local": CopilotMode.DETERMINISTIC,
        "offline": CopilotMode.DETERMINISTIC,
        "free": CopilotMode.DETERMINISTIC,
        "ai": CopilotMode.AI,
        "openai": CopilotMode.AI,
        "llm": CopilotMode.AI,
        "gpt": CopilotMode.AI,
        "auto": CopilotMode.AUTO,
        "automatic": CopilotMode.AUTO,
    }

    if normalized not in aliases:
        allowed = ", ".join(mode.value for mode in CopilotMode)
        raise ValueError(f"Unsupported copilot mode {value!r}. Use one of: {allowed}.")

    return aliases[normalized]
