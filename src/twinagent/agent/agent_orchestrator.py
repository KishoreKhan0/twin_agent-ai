"""Deterministic agentic copilot orchestrator for TwinAgent AI.

This MVP orchestrator does not call an external LLM. It demonstrates the agentic
workflow by calling tools, combining sensor evidence with retrieved engineering
documents, and producing a grounded maintenance explanation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import indent

from twinagent.agent.prompts import COPILOT_RESPONSE_POLICY
from twinagent.agent.tools import TwinAgentTools


@dataclass
class TwinAgentCopilot:
    """Tool-using copilot for incident explanation and maintenance guidance."""

    tools: TwinAgentTools

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "TwinAgentCopilot":
        """Create a copilot using the default project file layout."""
        root = Path(project_root)
        tools = TwinAgentTools(
            processed_data_path=root / "data" / "processed" / "sensor_data_with_anomalies.csv",
            incidents_path=root / "data" / "incidents" / "incidents.json",
            rag_config_path=root / "configs" / "rag_config.yaml",
            project_root=root,
        )
        return cls(tools=tools)

    def answer_incident_question(
        self,
        incident_id: str,
        question: str = "Why did this incident trigger?",
    ) -> str:
        """Answer an incident question using tool calls and retrieved documents."""
        incident = self.tools.get_incident(incident_id)

        window_summary = self.tools.summarize_sensor_window(
            machine_id=str(incident["machine_id"]),
            start_time=str(incident["start_time"]),
            end_time=str(incident["end_time"]),
            contributing_sensors=list(incident.get("contributing_sensors", [])),
        )

        retrieval_query = self._build_retrieval_query(question, incident, window_summary)
        retrieved_sources = self.tools.retrieve_knowledge(retrieval_query, top_k=4)
        checklist = self.tools.generate_maintenance_checklist(
            suspected_fault=str(incident["suspected_fault"]),
            severity=str(incident["severity"]),
        )

        return self._compose_answer(
            question=question,
            incident=incident,
            window_summary=window_summary,
            checklist=checklist,
            retrieved_sources=retrieved_sources,
        )

    @staticmethod
    def _build_retrieval_query(
        question: str,
        incident: dict,
        window_summary: dict,
    ) -> str:
        """Build a retrieval query from the question, fault, and sensor evidence."""
        contributing_sensors = " ".join(incident.get("contributing_sensors", []))
        evidence_terms = " ".join(window_summary.get("sensor_summary", {}).keys())

        return (
            f"{question} "
            f"{incident.get('suspected_fault', '')} "
            f"{incident.get('severity', '')} "
            f"{contributing_sensors} "
            f"{evidence_terms} "
            "maintenance inspection safety"
        )

    def _compose_answer(
        self,
        question: str,
        incident: dict,
        window_summary: dict,
        checklist: list[str],
        retrieved_sources: list,
    ) -> str:
        """Compose a grounded incident explanation."""
        lines: list[str] = []

        lines.append("# TwinAgent AI Copilot Answer")
        lines.append("")
        lines.append(f"**Question:** {question}")
        lines.append("")

        lines.append("## 1. Incident summary")
        lines.append(
            f"Incident `{incident['incident_id']}` was triggered for "
            f"`{incident['machine_id']}` from `{incident['start_time']}` to "
            f"`{incident['end_time']}`."
        )
        lines.append(
            f"The system classifies this as a **{incident['severity']}** severity incident "
            f"with suspected fault **{incident['suspected_fault']}**."
        )
        lines.append(
            f"The maximum anomaly score was **{incident['max_anomaly_score']}** and the "
            f"mean anomaly score was **{incident['mean_anomaly_score']}**."
        )
        lines.append("")

        lines.append("## 2. Sensor evidence")
        lines.append(
            f"The queried window contains **{window_summary['rows']}** rows. "
            f"The minimum health score in this window was "
            f"**{window_summary['min_health_score']}**."
        )
        lines.append("")

        for sensor, summary in window_summary["sensor_summary"].items():
            lines.append(
                f"- `{sensor}` ranged from **{summary['min']}** to **{summary['max']}** "
                f"(start **{summary['start']}**, end **{summary['end']}**, "
                f"change **{summary['change']}**)."
            )

        if incident.get("evidence"):
            lines.append("")
            lines.append("Incident-level evidence from the detector:")
            for sensor, evidence in incident["evidence"].items():
                lines.append(f"- `{sensor}`: {evidence}")

        lines.append("")

        lines.append("## 3. Engineering document guidance")
        if retrieved_sources:
            for index, source in enumerate(retrieved_sources, start=1):
                excerpt = self._shorten(source.text, max_chars=420)
                lines.append(
                    f"{index}. **{source.title} — {source.heading}** "
                    f"`[{source.citation}]`"
                )
                lines.append("")
                lines.append(indent(excerpt, prefix="   "))
                lines.append("")
        else:
            lines.append("No relevant knowledge-base source was retrieved.")
            lines.append("")

        lines.append("## 4. Recommended maintenance actions")
        for action in checklist:
            lines.append(f"- {action}")
        lines.append(f"- Current row-level recommendation: {window_summary['latest_maintenance_recommendation']}")
        lines.append("")

        lines.append("## 5. Uncertainty and limits")
        lines.append(
            "- This is a suspected fault based on synthetic sensor evidence and document retrieval, "
            "not physical confirmation."
        )
        lines.append(
            "- A technician inspection is required to confirm real bearing damage, belt misalignment, "
            "cooling failure, or electrical overload."
        )
        lines.append("- The copilot follows this response policy:")
        lines.append("")
        lines.append(indent(COPILOT_RESPONSE_POLICY, prefix="  "))
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _shorten(text: str, max_chars: int) -> str:
        """Shorten retrieved text for readable command-line output."""
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."
