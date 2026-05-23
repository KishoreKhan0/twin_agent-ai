"""Question intent routing for the TwinAgent AI copilot."""

from __future__ import annotations

from dataclasses import dataclass
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


def classify_copilot_question(question: str) -> IntentResult:
    """Classify a user question into one focused copilot intent."""
    normalized = _normalize(question)

    if not normalized:
        return IntentResult(CopilotIntent.INCIDENT_SUMMARY, 0.5, "Empty question defaults to summary.")

    if _is_irrelevant(normalized):
        return IntentResult(CopilotIntent.IRRELEVANT, 0.9, "Question is unrelated to machine incidents.")

    if _contains_any(normalized, [
        "full report", "complete report", "whole report", "entire report", "everything",
        "all details", "full explanation", "complete explanation", "give me the full", "give full",
    ]):
        return IntentResult(CopilotIntent.FULL_REPORT, 0.95, "Question asks for full report.")

    if _contains_any(normalized, [
        "what happened", "summarize", "summary", "brief", "overview",
        "incident summary", "tell me about the incident",
    ]):
        return IntentResult(CopilotIntent.INCIDENT_SUMMARY, 0.85, "Question asks for summary.")

    if _contains_any(normalized, [
        "when", "what time", "start time", "end time", "time of",
        "incident time", "duration", "how long", "time window",
    ]):
        return IntentResult(CopilotIntent.INCIDENT_TIME, 0.92, "Question asks about timing.")

    if _contains_any(normalized, [
        "current status", "latest status", "right now", "now", "current machine",
        "latest machine", "is it normal", "is machine healthy",
    ]):
        return IntentResult(CopilotIntent.CURRENT_STATUS, 0.88, "Question asks about latest machine state.")

    if _contains_any(normalized, [
        "which machine", "machine id", "machine name", "machine affected", "affected machine",
    ]) and not _contains_any(normalized, ["fault", "problem", "issue", "cause"]):
        return IntentResult(CopilotIntent.MACHINE_ID, 0.9, "Question asks which machine is affected.")

    if _contains_any(normalized, [
        "which fault", "what fault", "machine fault", "suspected fault", "fault type",
        "which problem", "what problem", "root cause", "cause", "why did", "why was",
        "why triggered", "triggered",
    ]):
        return IntentResult(CopilotIntent.MACHINE_FAULT, 0.88, "Question asks for suspected fault/cause.")

    if _contains_any(normalized, [
        "severity", "how severe", "critical", "high risk", "risk level", "priority",
    ]):
        return IntentResult(CopilotIntent.SEVERITY, 0.88, "Question asks about severity/risk.")

    if _contains_any(normalized, [
        "health", "health score", "machine health", "minimum health", "min health", "latest health",
    ]):
        return IntentResult(CopilotIntent.HEALTH_STATUS, 0.88, "Question asks about health score.")

    if _contains_any(normalized, [
        "anomaly score", "max anomaly", "mean anomaly", "anomaly", "score",
    ]):
        return IntentResult(CopilotIntent.ANOMALY_SCORE, 0.82, "Question asks about anomaly score.")

    if _contains_any(normalized, [
        "sensor", "evidence", "values", "temperature", "vibration", "current", "rpm",
        "throughput", "which sensors", "contributing sensors",
    ]):
        return IntentResult(CopilotIntent.SENSOR_EVIDENCE, 0.86, "Question asks about sensor evidence.")

    if _contains_any(normalized, [
        "inspect", "technician", "maintenance", "action", "recommend", "recommendation",
        "what should", "fix", "repair", "next step", "first check", "check first",
    ]):
        return IntentResult(CopilotIntent.MAINTENANCE_ACTION, 0.88, "Question asks for action.")

    if _contains_any(normalized, [
        "source", "sources", "document", "manual", "reference", "knowledge base", "why according to",
    ]):
        return IntentResult(CopilotIntent.ENGINEERING_SOURCES, 0.86, "Question asks for sources.")

    if _contains_any(normalized, [
        "incident", "machine", "motor", "bearing", "belt", "overheating", "maintenance",
    ]):
        return IntentResult(CopilotIntent.INCIDENT_SUMMARY, 0.65, "Broad project question.")

    return IntentResult(CopilotIntent.IRRELEVANT, 0.75, "No incident-related intent found.")


def _normalize(text: str) -> str:
    """Normalize question text for keyword matching."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9_+\-\s?]", " ", text)
    return re.sub(r"\s+", " ", text)


def _contains_any(text: str, phrases: list[str]) -> bool:
    """Return True if text contains any phrase."""
    return any(phrase in text for phrase in phrases)


def _is_irrelevant(text: str) -> bool:
    """Detect clearly irrelevant questions for this copilot."""
    irrelevant_terms = [
        "weather", "capital of", "president", "prime minister", "football", "cricket",
        "movie", "song", "recipe", "cook", "dating", "love", "joke", "poem",
        "translate", "summarize this article", "stock price", "bitcoin",
    ]
    project_terms = [
        "incident", "machine", "sensor", "fault", "maintenance", "health", "anomaly",
        "bearing", "belt", "motor", "temperature", "vibration", "current", "rpm",
        "throughput", "copilot",
    ]
    return any(term in text for term in irrelevant_terms) and not any(term in text for term in project_terms)
