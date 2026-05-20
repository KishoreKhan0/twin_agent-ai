"""Markdown incident report writer for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from textwrap import indent

from twinagent.agent.prompts import COPILOT_RESPONSE_POLICY
from twinagent.agent.tools import TwinAgentTools


@dataclass
class IncidentReportWriter:
    """Create evidence-grounded Markdown incident reports."""

    tools: TwinAgentTools

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "IncidentReportWriter":
        """Create a report writer using the default project file layout."""
        root = Path(project_root)
        tools = TwinAgentTools(
            processed_data_path=root / "data" / "processed" / "sensor_data_with_anomalies.csv",
            incidents_path=root / "data" / "incidents" / "incidents.json",
            rag_config_path=root / "configs" / "rag_config.yaml",
            project_root=root,
        )
        return cls(tools=tools)

    def generate_report_markdown(
        self,
        incident_id: str,
        question: str | None = None,
    ) -> str:
        """Generate a Markdown report for an incident."""
        incident = self.tools.get_incident(incident_id)
        question = question or (
            "Why did this incident trigger and what should the technician inspect first?"
        )

        window_summary = self.tools.summarize_sensor_window(
            machine_id=str(incident["machine_id"]),
            start_time=str(incident["start_time"]),
            end_time=str(incident["end_time"]),
            contributing_sensors=list(incident.get("contributing_sensors", [])),
        )

        retrieval_query = self._build_retrieval_query(question, incident, window_summary)
        retrieved_sources = self.tools.retrieve_knowledge(retrieval_query, top_k=5)
        checklist = self.tools.generate_maintenance_checklist(
            suspected_fault=str(incident["suspected_fault"]),
            severity=str(incident["severity"]),
        )

        lines: list[str] = [
            f"# Incident Report: {incident['incident_id']}",
            "",
            "## Executive summary",
            "",
            (
                f"Incident `{incident['incident_id']}` affected machine "
                f"`{incident['machine_id']}` between `{incident['start_time']}` and "
                f"`{incident['end_time']}`."
            ),
            (
                f"The system classified the event as **{incident['severity']}** severity "
                f"with suspected fault **{incident['suspected_fault']}**."
            ),
            (
                f"The maximum anomaly score was **{incident['max_anomaly_score']}** and "
                f"the mean anomaly score was **{incident['mean_anomaly_score']}**."
            ),
            "",
            "## Machine health and maintenance status",
            "",
            f"- Minimum health score in incident window: **{window_summary['min_health_score']}**",
            f"- Latest health score in incident window: **{window_summary['latest_health_score']}**",
            f"- Latest risk level in incident window: **{window_summary['latest_risk_level']}**",
            (
                "- Latest maintenance urgency in incident window: "
                f"**{window_summary['latest_maintenance_urgency']}**"
            ),
            (
                "- Latest row-level maintenance recommendation: "
                f"{window_summary['latest_maintenance_recommendation']}"
            ),
            "",
            "## Sensor evidence",
            "",
            (
                f"The queried sensor window contains **{window_summary['rows']}** rows "
                f"from `{window_summary['time_range']['start']}` to "
                f"`{window_summary['time_range']['end']}`."
            ),
            "",
        ]

        for sensor, summary in window_summary["sensor_summary"].items():
            lines.append(
                f"- `{sensor}` ranged from **{summary['min']}** to **{summary['max']}** "
                f"(start **{summary['start']}**, end **{summary['end']}**, "
                f"change **{summary['change']}**)."
            )

        lines.extend(["", "### Detector evidence", ""])

        for sensor, evidence in incident.get("evidence", {}).items():
            lines.append(f"- `{sensor}`: {evidence}")

        lines.extend(["", "## Retrieved engineering references", ""])

        if retrieved_sources:
            for index, source in enumerate(retrieved_sources, start=1):
                excerpt = self._shorten(source.text, max_chars=520)
                lines.append(
                    f"{index}. **{source.title} — {source.heading}** "
                    f"`[{source.citation}]`"
                )
                lines.append("")
                lines.append(indent(excerpt, prefix="   "))
                lines.append("")
        else:
            lines.append("No relevant engineering reference was retrieved.")
            lines.append("")

        lines.extend(["## Recommended technician actions", ""])

        for action in checklist:
            lines.append(f"- {action}")

        lines.extend(
            [
                "",
                "## Uncertainty and limitations",
                "",
                (
                    "- This report describes a suspected fault based on synthetic sensor data, "
                    "detector output, and retrieved engineering documents."
                ),
                (
                    "- The system cannot physically confirm bearing damage, belt misalignment, "
                    "cooling failure, or electrical overload without technician inspection."
                ),
                (
                    "- This is not a certified safety system or production-grade "
                    "predictive-maintenance system."
                ),
                "",
                "## Copilot response policy",
                "",
                indent(COPILOT_RESPONSE_POLICY, prefix="  "),
                "",
            ]
        )

        return "\n".join(lines)

    def write_report(
        self,
        incident_id: str,
        output_dir: str | Path,
        question: str | None = None,
    ) -> Path:
        """Generate and write a Markdown report for an incident."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        safe_incident_id = _safe_filename(incident_id)
        report_path = output_path / f"{safe_incident_id}_report.md"
        report = self.generate_report_markdown(incident_id=incident_id, question=question)
        report_path.write_text(report, encoding="utf-8")

        return report_path

    @staticmethod
    def _build_retrieval_query(
        question: str,
        incident: dict,
        window_summary: dict,
    ) -> str:
        """Build a retrieval query from incident context."""
        contributing_sensors = " ".join(incident.get("contributing_sensors", []))
        sensor_terms = " ".join(window_summary.get("sensor_summary", {}).keys())

        return (
            f"{question} "
            f"{incident.get('suspected_fault', '')} "
            f"{incident.get('severity', '')} "
            f"{contributing_sensors} {sensor_terms} "
            "maintenance procedure safety inspection"
        )

    @staticmethod
    def _shorten(text: str, max_chars: int) -> str:
        """Shorten retrieved text for readable reports."""
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."


def _safe_filename(value: str) -> str:
    """Return a filesystem-safe filename stem."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
