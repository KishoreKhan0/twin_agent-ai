"""Context builder for AI-backed TwinAgent copilot answers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from twinagent.agent.question_intent import CopilotIntent


@dataclass(frozen=True)
class CopilotContextPackage:
    """Context package sent to the LLM provider."""

    intent: CopilotIntent
    context: dict[str, Any]

    def to_json(self) -> str:
        """Serialize context package for prompt use."""
        return json.dumps(
            {
                "intent": self.intent.value,
                "context": self.context,
            },
            indent=2,
            default=str,
            sort_keys=True,
        )


@dataclass
class CopilotContextBuilder:
    """Build minimal question-specific context from trusted TwinAgent tools."""

    tools: Any

    def build(
        self,
        question: str,
        incident: dict,
        intent: CopilotIntent,
        memory_items: list[dict] | None = None,
    ) -> CopilotContextPackage:
        """Build context tailored to a classified question intent."""
        base_context: dict[str, Any] = {
            "question": question,
            "incident": {
                "incident_id": incident.get("incident_id"),
                "machine_id": incident.get("machine_id"),
                "start_time": incident.get("start_time"),
                "end_time": incident.get("end_time"),
                "duration_seconds": incident.get("duration_seconds"),
                "severity": incident.get("severity"),
                "suspected_fault": incident.get("suspected_fault"),
                "max_anomaly_score": incident.get("max_anomaly_score"),
                "mean_anomaly_score": incident.get("mean_anomaly_score"),
                "contributing_sensors": incident.get("contributing_sensors", []),
                "detector_evidence": incident.get("evidence", {}),
            },
            "memory": _trim_memory(memory_items or []),
            "rules": [
                "Answer only the user's question.",
                "Do not dump the full incident report unless the intent is full_report.",
                "Use only the provided context.",
                "If the context is insufficient, say what is unavailable.",
                "Use 'suspected fault' unless physical inspection has confirmed the fault.",
                "Keep short factual answers to one or two sentences.",
            ],
        }

        if intent in {
            CopilotIntent.FULL_REPORT,
            CopilotIntent.MACHINE_FAULT,
            CopilotIntent.HEALTH_STATUS,
            CopilotIntent.SENSOR_EVIDENCE,
            CopilotIntent.MAINTENANCE_ACTION,
        }:
            base_context["sensor_window_summary"] = self._window_summary(incident)

        if intent in {
            CopilotIntent.FULL_REPORT,
            CopilotIntent.MAINTENANCE_ACTION,
            CopilotIntent.ENGINEERING_SOURCES,
        }:
            base_context["engineering_sources"] = self._retrieved_sources(
                question=question,
                incident=incident,
                top_k=4 if intent == CopilotIntent.FULL_REPORT else 3,
            )

        if intent == CopilotIntent.CURRENT_STATUS:
            base_context["latest_machine_status"] = self._latest_status()

        if intent == CopilotIntent.MAINTENANCE_ACTION:
            base_context["maintenance_checklist"] = self.tools.generate_maintenance_checklist(
                suspected_fault=str(incident.get("suspected_fault", "")),
                severity=str(incident.get("severity", "")),
            )

        return CopilotContextPackage(intent=intent, context=base_context)

    def _window_summary(self, incident: dict) -> dict:
        """Return incident-window summary."""
        return self.tools.summarize_sensor_window(
            machine_id=str(incident["machine_id"]),
            start_time=str(incident["start_time"]),
            end_time=str(incident["end_time"]),
            contributing_sensors=list(incident.get("contributing_sensors", [])),
        )

    def _retrieved_sources(self, question: str, incident: dict, top_k: int) -> list[dict]:
        """Return compact retrieved engineering source information."""
        query = (
            f"{question} {incident.get('suspected_fault', '')} "
            f"{' '.join(incident.get('contributing_sensors', []))} "
            "maintenance inspection safety"
        )
        results = self.tools.retrieve_knowledge(query, top_k=top_k)

        return [
            {
                "citation": result.citation,
                "title": result.title,
                "heading": result.heading,
                "text": " ".join(result.text.split())[:700],
            }
            for result in results
        ]

    def _latest_status(self) -> dict:
        """Return latest machine status from processed data."""
        dataframe = self.tools.load_processed_data()
        latest = dataframe.sort_values("timestamp").iloc[-1]

        return {
            "timestamp": latest["timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
            "machine_id": latest["machine_id"],
            "machine_state": latest["machine_state"],
            "health_score": int(latest["health_score"]),
            "risk_level": latest["risk_level"],
            "maintenance_urgency": latest["maintenance_urgency"],
            "maintenance_recommendation": latest["maintenance_recommendation"],
        }


def _trim_memory(items: list[dict]) -> list[dict]:
    """Keep memory concise before sending to the LLM."""
    trimmed: list[dict] = []
    for item in items[:5]:
        trimmed.append(
            {
                "created_at": item.get("created_at"),
                "incident_id": item.get("incident_id"),
                "question": item.get("question"),
                "answer": str(item.get("answer", ""))[:500],
                "intent": item.get("intent"),
            }
        )
    return trimmed
