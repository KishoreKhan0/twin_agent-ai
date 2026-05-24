"""Question intent routing for the TwinAgent AI copilot.

This module intentionally stays lightweight and dependency-free. It supports
structured questions and messy short questions such as:

- "issue when?"
- "wat happend bro"
- "what wrong with motor"
- "is it bad?"
- "what should i do now?"

Important priority rule:
Specific operational intents must win over generic phrase matches. For example:
- "Which machine fault happened?" means machine_fault, not machine_id.
- "What should I do now?" means maintenance_action, not current_status.
- "What is the current machine status?" means current_status, not sensor_evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
import re


class CopilotIntent(str, Enum):
    """Supported copilot question intents."""

    FULL_REPORT = "full_report"
    INCIDENT_SUMMARY = "incident_summary"
    INCIDENT_TIME = "incident_time"
    MACHINE_FAULT = "machine_fault"
    MACHINE_ID = "machine_id"
    SEVERITY = "severity"
    HEALTH_STATUS = "health_status"
    ANOMALY_SCORE = "anomaly_score"
    SENSOR_EVIDENCE = "sensor_evidence"
    MAINTENANCE_ACTION = "maintenance_action"
    ENGINEERING_SOURCES = "engineering_sources"
    CURRENT_STATUS = "current_status"
    IRRELEVANT = "irrelevant"


@dataclass(frozen=True)
class IntentResult:
    """Result of lightweight question-intent classification."""

    intent: CopilotIntent
    confidence: float
    reason: str


INTENT_PATTERNS: dict[CopilotIntent, list[str]] = {
    CopilotIntent.FULL_REPORT: [
        "full report",
        "complete report",
        "whole report",
        "entire report",
        "everything",
        "all details",
        "full explanation",
        "complete explanation",
        "give me the full",
        "give full",
        "show all",
    ],
    CopilotIntent.MAINTENANCE_ACTION: [
        "inspect",
        "technician",
        "maintenance",
        "action",
        "recommend",
        "recommendation",
        "what should",
        "what should i do",
        "what should we do",
        "what do i do",
        "what do we do",
        "what can i do",
        "fix",
        "repair",
        "next step",
        "next steps",
        "first check",
        "check first",
        "do now",
        "what now",
        "what should i do now",
        "solve",
        "handle this",
    ],
    CopilotIntent.MACHINE_FAULT: [
        "which fault",
        "what fault",
        "machine fault",
        "suspected fault",
        "fault type",
        "which problem",
        "what problem",
        "root cause",
        "cause",
        "why did",
        "why was",
        "why triggered",
        "triggered",
        "what wrong",
        "what is wrong",
        "what wrong with motor",
        "issue cause",
    ],
    CopilotIntent.CURRENT_STATUS: [
        "current status",
        "latest status",
        "right now",
        "current machine",
        "current machine status",
        "latest machine",
        "latest machine status",
        "is it normal",
        "is machine healthy",
        "currently",
        "status now",
        "how is it now",
    ],
    CopilotIntent.INCIDENT_TIME: [
        "when",
        "when did",
        "what time",
        "start time",
        "end time",
        "time of",
        "incident time",
        "issue time",
        "problem time",
        "duration",
        "how long",
        "time window",
        "issue when",
        "when happened",
    ],
    CopilotIntent.SEVERITY: [
        "severity",
        "how severe",
        "critical",
        "high risk",
        "risk level",
        "priority",
        "is it bad",
        "how bad",
        "bad is it",
        "dangerous",
        "urgent",
    ],
    CopilotIntent.SENSOR_EVIDENCE: [
        "sensor",
        "evidence",
        "values",
        "temperature",
        "vibration",
        "electrical current",
        "motor current",
        "current_a",
        "rpm",
        "throughput",
        "which sensors",
        "contributing sensors",
        "proof",
        "show evidence",
        "sensor proof",
    ],
    CopilotIntent.HEALTH_STATUS: [
        "health",
        "health score",
        "machine health",
        "minimum health",
        "min health",
        "latest health",
        "healthy",
    ],
    CopilotIntent.ANOMALY_SCORE: [
        "anomaly score",
        "max anomaly",
        "mean anomaly",
        "anomaly",
        "score",
        "abnormal score",
    ],
    CopilotIntent.ENGINEERING_SOURCES: [
        "source",
        "sources",
        "document",
        "manual",
        "reference",
        "knowledge base",
        "why according to",
        "docs",
        "where from",
    ],
    CopilotIntent.INCIDENT_SUMMARY: [
        "what happened",
        "wat happend",
        "what happen",
        "summarize",
        "summary",
        "brief",
        "overview",
        "incident summary",
        "tell me about the incident",
        "tell me something",
        "what is going on",
        "what went wrong",
        "explain incident",
    ],
    CopilotIntent.MACHINE_ID: [
        "which machine",
        "machine id",
        "machine name",
        "machine affected",
        "affected machine",
        "which asset",
        "asset id",
    ],
}


DIRECT_MATCH_PRIORITY: list[CopilotIntent] = [
    CopilotIntent.FULL_REPORT,
    CopilotIntent.MAINTENANCE_ACTION,
    CopilotIntent.MACHINE_FAULT,
    CopilotIntent.CURRENT_STATUS,
    CopilotIntent.INCIDENT_TIME,
    CopilotIntent.SEVERITY,
    CopilotIntent.SENSOR_EVIDENCE,
    CopilotIntent.HEALTH_STATUS,
    CopilotIntent.ANOMALY_SCORE,
    CopilotIntent.ENGINEERING_SOURCES,
    CopilotIntent.INCIDENT_SUMMARY,
    CopilotIntent.MACHINE_ID,
]


def classify_copilot_question(question: str) -> IntentResult:
    """Classify a user question into one focused copilot intent."""
    normalized = _normalize(question)

    if not normalized:
        return IntentResult(CopilotIntent.INCIDENT_SUMMARY, 0.5, "Empty question defaults to summary.")

    if _is_irrelevant(normalized):
        return IntentResult(CopilotIntent.IRRELEVANT, 0.9, "Question is unrelated to machine incidents.")

    forced = _forced_specific_intent(normalized)
    if forced is not None:
        return forced

    direct = _direct_match(normalized)
    if direct is not None:
        return direct

    fuzzy = _fuzzy_match(normalized)
    if fuzzy is not None:
        return fuzzy

    if _contains_any(
        normalized,
        [
            "incident",
            "machine",
            "motor",
            "bearing",
            "belt",
            "overheating",
            "maintenance",
            "issue",
            "problem",
            "fault",
        ],
    ):
        return IntentResult(
            CopilotIntent.INCIDENT_SUMMARY,
            0.62,
            "Broad project-related question defaults to concise incident summary.",
        )

    return IntentResult(CopilotIntent.IRRELEVANT, 0.75, "No incident-related intent found.")


def suggested_followups_for_intent(intent: CopilotIntent) -> list[str]:
    """Return useful follow-up questions for a given intent."""
    mapping = {
        CopilotIntent.INCIDENT_TIME: [
            "Which machine was affected?",
            "How severe was the incident?",
            "What caused it?",
        ],
        CopilotIntent.MACHINE_FAULT: [
            "What sensor evidence supports this?",
            "What should the technician inspect first?",
            "How severe is it?",
        ],
        CopilotIntent.SEVERITY: [
            "What is the health score?",
            "What should we do now?",
            "Which sensors contributed?",
        ],
        CopilotIntent.SENSOR_EVIDENCE: [
            "What fault does this indicate?",
            "What should the technician inspect first?",
            "Give me the full report.",
        ],
        CopilotIntent.MAINTENANCE_ACTION: [
            "Which sensors support this action?",
            "What engineering sources support this?",
            "Give me the full report.",
        ],
        CopilotIntent.CURRENT_STATUS: [
            "Was there an incident earlier?",
            "What is the latest health score?",
            "What should the technician inspect first?",
        ],
        CopilotIntent.IRRELEVANT: [
            "What happened in the incident?",
            "What is the current machine status?",
            "What should the technician inspect first?",
        ],
    }
    return mapping.get(
        intent,
        [
            "When did the incident happen?",
            "Which fault was suspected?",
            "What should the technician inspect first?",
        ],
    )


def _forced_specific_intent(text: str) -> IntentResult | None:
    """Handle ambiguous phrases where specific intent must override generic keywords."""
    # "What is the current machine status?" contains "current", but it is asking status.
    if _contains_any(
        text,
        [
            "current status",
            "current machine status",
            "latest status",
            "latest machine status",
            "status now",
            "how is it now",
            "is it normal",
        ],
    ):
        return IntentResult(
            CopilotIntent.CURRENT_STATUS,
            0.95,
            "Current/latest status wording overrides sensor evidence.",
        )

    # "Which machine fault happened?" contains "which machine", but the key request is fault.
    if _contains_any(text, ["fault", "problem", "cause", "wrong", "trigger"]):
        if _contains_any(text, ["which machine", "what machine", "machine fault", "what wrong", "what is wrong"]):
            return IntentResult(
                CopilotIntent.MACHINE_FAULT,
                0.93,
                "Fault/problem wording overrides generic machine identification.",
            )

    # "What should I do now?" contains "now", but the key request is action.
    if _contains_any(
        text,
        [
            "what should i do",
            "what should we do",
            "what do i do",
            "what do we do",
            "what can i do",
            "do now",
            "what now",
            "next step",
            "fix",
            "repair",
            "inspect",
        ],
    ):
        return IntentResult(
            CopilotIntent.MAINTENANCE_ACTION,
            0.94,
            "Action wording overrides generic current-status wording.",
        )

    return None


def _direct_match(text: str) -> IntentResult | None:
    """Classify by direct phrase matching with explicit priority."""
    for intent in DIRECT_MATCH_PRIORITY:
        for pattern in INTENT_PATTERNS[intent]:
            if pattern in text:
                return IntentResult(intent, 0.9, f"Matched phrase: {pattern!r}.")
    return None


def _fuzzy_match(text: str) -> IntentResult | None:
    """Classify by fuzzy similarity against known messy phrases."""
    if len(text) < 4:
        return None

    best_intent: CopilotIntent | None = None
    best_pattern = ""
    best_score = 0.0

    for intent in DIRECT_MATCH_PRIORITY:
        for pattern in INTENT_PATTERNS[intent]:
            score = _similarity(text, pattern)

            # Also compare against important short windows in a longer question.
            for window in _token_windows(text, max_tokens=5):
                score = max(score, _similarity(window, pattern))

            if score > best_score:
                best_intent = intent
                best_pattern = pattern
                best_score = score

    if best_intent is not None and best_score >= 0.74:
        return IntentResult(
            best_intent,
            round(best_score, 2),
            f"Fuzzy matched phrase: {best_pattern!r}.",
        )

    return None


def _normalize(text: str) -> str:
    """Normalize question text for keyword and fuzzy matching."""
    text = text.lower().strip()
    replacements = {
        "wht": "what",
        "wat": "what",
        "happend": "happened",
        "hapen": "happen",
        "prob": "problem",
        "pls": "please",
        "plz": "please",
        "machin": "machine",
        "motr": "motor",
    }

    text = re.sub(r"[^a-z0-9_+\-\s?]", " ", text)
    words = [replacements.get(word, word) for word in text.split()]
    return re.sub(r"\s+", " ", " ".join(words)).strip()


def _contains_any(text: str, phrases: list[str]) -> bool:
    """Return True if text contains any phrase."""
    return any(phrase in text for phrase in phrases)


def _similarity(left: str, right: str) -> float:
    """Return a simple similarity ratio."""
    return SequenceMatcher(None, left, right).ratio()


def _token_windows(text: str, max_tokens: int) -> list[str]:
    """Return short token windows for fuzzy matching longer questions."""
    tokens = text.split()
    windows: list[str] = []
    for size in range(1, min(max_tokens, len(tokens)) + 1):
        for start in range(0, len(tokens) - size + 1):
            windows.append(" ".join(tokens[start:start + size]))
    return windows


def _is_irrelevant(text: str) -> bool:
    """Detect clearly irrelevant questions for this copilot."""
    irrelevant_terms = [
        "weather",
        "capital of",
        "president",
        "prime minister",
        "football",
        "cricket",
        "movie",
        "song",
        "recipe",
        "cook",
        "dating",
        "love",
        "joke",
        "poem",
        "translate",
        "summarize this article",
        "stock price",
        "bitcoin",
    ]
    project_terms = [
        "incident",
        "machine",
        "sensor",
        "fault",
        "maintenance",
        "health",
        "anomaly",
        "bearing",
        "belt",
        "motor",
        "temperature",
        "vibration",
        "current",
        "rpm",
        "throughput",
        "copilot",
        "issue",
        "problem",
    ]
    return any(term in text for term in irrelevant_terms) and not any(term in text for term in project_terms)
