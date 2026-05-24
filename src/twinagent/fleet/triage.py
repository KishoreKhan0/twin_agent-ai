"""Fleet-level maintenance triage for TwinAgent AI.

This module ranks machines and incidents by operational priority using fleet
summary data. It is deterministic, explainable, and does not require external AI.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


SEVERITY_WEIGHT = {
    "critical": 100,
    "high": 80,
    "medium": 55,
    "low": 30,
    "none": 0,
}

FAULT_WEIGHT = {
    "bearing_wear": 22,
    "overheating": 18,
    "belt_misalignment": 15,
    "current_anomaly": 10,
    "unknown_anomaly": 8,
}


@dataclass(frozen=True)
class IncidentTriageResult:
    """Priority result for one fleet incident."""

    incident_id: str
    machine_id: str
    line_id: str
    severity: str
    suspected_fault: str
    priority_score: float
    priority_level: str
    start_time: str
    end_time: str
    duration_seconds: int
    max_anomaly_score: float
    contributing_sensors: list[str]
    reason: str


@dataclass(frozen=True)
class MachineTriageResult:
    """Priority result for one fleet machine."""

    machine_id: str
    line_id: str
    display_name: str
    priority_score: float
    priority_level: str
    incident_count: int
    high_incident_count: int
    minimum_health_score: int
    anomaly_rows: int
    suspected_faults: list[str]
    recommended_action: str
    reason: str


@dataclass(frozen=True)
class FleetTriageResult:
    """Fleet-level triage output."""

    fleet_machine_count: int
    fleet_incident_count: int
    fleet_time_start: str
    fleet_time_end: str
    top_machine: MachineTriageResult | None
    top_incident: IncidentTriageResult | None
    machine_triage: list[MachineTriageResult]
    incident_triage: list[IncidentTriageResult]


def build_fleet_triage(summary: dict[str, Any]) -> FleetTriageResult:
    """Build deterministic fleet triage from fleet summary JSON data."""
    fleet = summary.get("fleet", {})
    machines = summary.get("machines", [])
    incidents = summary.get("incidents", [])

    incident_results = [_triage_incident(incident) for incident in incidents]
    incident_results = sorted(
        incident_results,
        key=lambda item: (item.priority_score, item.start_time),
        reverse=True,
    )

    machine_results = [
        _triage_machine(machine=machine, incidents=incident_results)
        for machine in machines
    ]
    machine_results = sorted(
        machine_results,
        key=lambda item: (item.priority_score, item.machine_id),
        reverse=True,
    )

    top_machine = machine_results[0] if machine_results else None
    top_incident = incident_results[0] if incident_results else None

    return FleetTriageResult(
        fleet_machine_count=int(fleet.get("machine_count", len(machines))),
        fleet_incident_count=int(fleet.get("incident_rows", len(incidents))),
        fleet_time_start=str(fleet.get("time_start", "")),
        fleet_time_end=str(fleet.get("time_end", "")),
        top_machine=top_machine,
        top_incident=top_incident,
        machine_triage=machine_results,
        incident_triage=incident_results,
    )


def export_fleet_triage_report(
    summary_path: str | Path,
    output_json_path: str | Path,
    output_markdown_path: str | Path,
) -> FleetTriageResult:
    """Read fleet summary and export JSON + Markdown triage reports."""
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    triage = build_fleet_triage(summary)

    output_json = Path(output_json_path)
    output_markdown = Path(output_markdown_path)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(_triage_to_dict(triage), indent=2),
        encoding="utf-8",
    )
    output_markdown.write_text(
        triage_to_markdown(triage),
        encoding="utf-8",
    )

    return triage


def triage_to_markdown(triage: FleetTriageResult) -> str:
    """Convert fleet triage result to Markdown."""
    lines = [
        "# TwinAgent AI Fleet Triage Report",
        "",
        "## Fleet scope",
        "",
        f"- Machines: {triage.fleet_machine_count}",
        f"- Incidents: {triage.fleet_incident_count}",
        f"- Time range: `{triage.fleet_time_start}` to `{triage.fleet_time_end}`",
        "",
    ]

    if triage.top_machine:
        lines.extend(
            [
                "## Top maintenance priority",
                "",
                f"- Machine: `{triage.top_machine.machine_id}`",
                f"- Priority level: **{triage.top_machine.priority_level}**",
                f"- Priority score: **{triage.top_machine.priority_score}**",
                f"- Recommended action: {triage.top_machine.recommended_action}",
                f"- Reason: {triage.top_machine.reason}",
                "",
            ]
        )

    if triage.top_incident:
        lines.extend(
            [
                "## Highest-priority incident",
                "",
                f"- Incident: `{triage.top_incident.incident_id}`",
                f"- Machine: `{triage.top_incident.machine_id}`",
                f"- Severity: **{triage.top_incident.severity}**",
                f"- Fault: **{triage.top_incident.suspected_fault}**",
                f"- Priority score: **{triage.top_incident.priority_score}**",
                f"- Reason: {triage.top_incident.reason}",
                "",
            ]
        )

    lines.extend(
        [
            "## Machine triage",
            "",
            "| Rank | Machine | Line | Priority | Score | Incidents | High incidents | Min health | Suspected faults | Recommended action |",
            "|---:|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for rank, machine in enumerate(triage.machine_triage, start=1):
        lines.append(
            "| "
            f"{rank} | "
            f"{machine.machine_id} | "
            f"{machine.line_id} | "
            f"{machine.priority_level} | "
            f"{machine.priority_score} | "
            f"{machine.incident_count} | "
            f"{machine.high_incident_count} | "
            f"{machine.minimum_health_score} | "
            f"{', '.join(machine.suspected_faults) or 'none'} | "
            f"{machine.recommended_action} |"
        )

    lines.extend(
        [
            "",
            "## Incident triage",
            "",
            "| Rank | Incident | Machine | Severity | Fault | Score | Duration | Max anomaly | Sensors |",
            "|---:|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for rank, incident in enumerate(triage.incident_triage, start=1):
        lines.append(
            "| "
            f"{rank} | "
            f"{incident.incident_id} | "
            f"{incident.machine_id} | "
            f"{incident.severity} | "
            f"{incident.suspected_fault} | "
            f"{incident.priority_score} | "
            f"{incident.duration_seconds} | "
            f"{incident.max_anomaly_score} | "
            f"{', '.join(incident.contributing_sensors)} |"
        )

    lines.append("")
    return "\n".join(lines)


def _triage_incident(incident: dict[str, Any]) -> IncidentTriageResult:
    """Score one incident."""
    severity = str(incident.get("severity", "none")).lower()
    suspected_fault = str(incident.get("suspected_fault", "unknown_anomaly"))
    max_anomaly_score = float(incident.get("max_anomaly_score", 0.0))
    duration_seconds = int(incident.get("duration_seconds", 0))
    sensors = list(incident.get("contributing_sensors", []))

    score = 0.0
    score += SEVERITY_WEIGHT.get(severity, 20)
    score += FAULT_WEIGHT.get(suspected_fault, 6)
    score += min(max_anomaly_score * 35, 35)
    score += min(duration_seconds / 120, 20)
    score += min(len(sensors) * 4, 16)

    priority_score = round(score, 2)
    priority_level = _priority_level(priority_score)

    reason = (
        f"{severity} severity, suspected {suspected_fault}, max anomaly "
        f"{max_anomaly_score}, duration {duration_seconds}s, "
        f"{len(sensors)} contributing sensor(s)."
    )

    return IncidentTriageResult(
        incident_id=str(incident.get("incident_id", "")),
        machine_id=str(incident.get("machine_id", "")),
        line_id=str(incident.get("line_id", "unknown")),
        severity=severity,
        suspected_fault=suspected_fault,
        priority_score=priority_score,
        priority_level=priority_level,
        start_time=str(incident.get("start_time", "")),
        end_time=str(incident.get("end_time", "")),
        duration_seconds=duration_seconds,
        max_anomaly_score=round(max_anomaly_score, 4),
        contributing_sensors=sensors,
        reason=reason,
    )


def _triage_machine(
    machine: dict[str, Any],
    incidents: list[IncidentTriageResult],
) -> MachineTriageResult:
    """Score one machine using machine summary and its incidents."""
    machine_id = str(machine.get("machine_id", ""))
    machine_incidents = [incident for incident in incidents if incident.machine_id == machine_id]
    high_incidents = [incident for incident in machine_incidents if incident.severity in {"high", "critical"}]
    incident_score = sum(incident.priority_score for incident in machine_incidents)
    minimum_health = int(machine.get("minimum_health_score", 100))
    anomaly_rows = int(machine.get("anomaly_rows", 0))
    suspected_faults = list(machine.get("suspected_faults", []))

    score = 0.0
    score += min(incident_score / 2, 120)
    score += len(machine_incidents) * 10
    score += len(high_incidents) * 18
    score += max(0, 100 - minimum_health) * 0.8
    score += min(anomaly_rows / 40, 35)
    score += len(suspected_faults) * 8

    priority_score = round(score, 2)
    priority_level = _priority_level(priority_score)
    action = _machine_action(priority_level, high_incidents, suspected_faults)

    reason = (
        f"{len(machine_incidents)} incident(s), {len(high_incidents)} high-severity incident(s), "
        f"minimum health {minimum_health}, {anomaly_rows} anomaly row(s), "
        f"suspected faults: {', '.join(suspected_faults) or 'none'}."
    )

    return MachineTriageResult(
        machine_id=machine_id,
        line_id=str(machine.get("line_id", "unknown")),
        display_name=str(machine.get("display_name", machine_id)),
        priority_score=priority_score,
        priority_level=priority_level,
        incident_count=int(machine.get("incident_count", len(machine_incidents))),
        high_incident_count=len(high_incidents),
        minimum_health_score=minimum_health,
        anomaly_rows=anomaly_rows,
        suspected_faults=suspected_faults,
        recommended_action=action,
        reason=reason,
    )


def _priority_level(score: float) -> str:
    """Map numeric score to priority level."""
    if score >= 170:
        return "critical"
    if score >= 120:
        return "high"
    if score >= 75:
        return "medium"
    if score >= 35:
        return "watch"
    return "normal"


def _machine_action(
    priority_level: str,
    high_incidents: list[IncidentTriageResult],
    suspected_faults: list[str],
) -> str:
    """Return deterministic maintenance action for a machine."""
    if priority_level == "critical":
        return "Stop machine if still active and perform immediate inspection."
    if priority_level == "high":
        if "bearing_wear" in suspected_faults:
            return "Prioritize bearing inspection, vibration check, lubrication review, and thermal inspection."
        return "Inspect within 24 hours and verify the highest-severity incident evidence."
    if priority_level == "medium":
        return "Schedule maintenance review within 48 hours and monitor repeated anomalies."
    if priority_level == "watch":
        return "Keep under watch and review if anomalies repeat."
    return "Continue normal monitoring."


def _triage_to_dict(triage: FleetTriageResult) -> dict[str, Any]:
    """Convert triage result dataclasses to dictionaries."""
    return {
        "fleet_machine_count": triage.fleet_machine_count,
        "fleet_incident_count": triage.fleet_incident_count,
        "fleet_time_start": triage.fleet_time_start,
        "fleet_time_end": triage.fleet_time_end,
        "top_machine": asdict(triage.top_machine) if triage.top_machine else None,
        "top_incident": asdict(triage.top_incident) if triage.top_incident else None,
        "machine_triage": [asdict(item) for item in triage.machine_triage],
        "incident_triage": [asdict(item) for item in triage.incident_triage],
    }
