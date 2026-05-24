"""Global fleet incident analysis and question answering.

This module answers across the full fleet, not one selected incident. It supports
questions such as:

- Which machine is worst?
- Compare bearing wear incidents.
- Show current anomaly incidents.
- Why is line1_motor2 critical?
- Which issue appears most often?
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Any


@dataclass(frozen=True)
class FaultPattern:
    """Aggregated pattern for one suspected fault."""

    suspected_fault: str
    incident_count: int
    machines: list[str]
    severity_counts: dict[str, int]
    average_duration_seconds: float
    max_anomaly_score: float
    common_sensors: list[str]
    incident_ids: list[str]


@dataclass(frozen=True)
class FleetQuestionAnswer:
    """Answer to a global fleet question."""

    question: str
    intent: str
    answer: str
    evidence: list[str]
    suggested_followups: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable answer."""
        return asdict(self)


def load_fleet_summary(path: str | Path) -> dict[str, Any]:
    """Load fleet summary JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze_fault_patterns(summary: dict[str, Any]) -> list[FaultPattern]:
    """Aggregate incidents by suspected fault."""
    incidents = list(summary.get("incidents", []))
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for incident in incidents:
        groups[str(incident.get("suspected_fault", "unknown_anomaly"))].append(incident)

    patterns: list[FaultPattern] = []
    for fault, items in groups.items():
        severity_counts = Counter(str(item.get("severity", "unknown")) for item in items)
        sensor_counts = Counter(
            sensor
            for item in items
            for sensor in item.get("contributing_sensors", [])
        )
        durations = [int(item.get("duration_seconds", 0)) for item in items]
        anomaly_scores = [float(item.get("max_anomaly_score", 0.0)) for item in items]

        patterns.append(
            FaultPattern(
                suspected_fault=fault,
                incident_count=len(items),
                machines=sorted({str(item.get("machine_id", "")) for item in items}),
                severity_counts=dict(sorted(severity_counts.items())),
                average_duration_seconds=round(sum(durations) / len(durations), 2) if durations else 0.0,
                max_anomaly_score=round(max(anomaly_scores), 4) if anomaly_scores else 0.0,
                common_sensors=[sensor for sensor, _ in sensor_counts.most_common(5)],
                incident_ids=[str(item.get("incident_id", "")) for item in items],
            )
        )

    return sorted(
        patterns,
        key=lambda pattern: (pattern.incident_count, pattern.max_anomaly_score),
        reverse=True,
    )


def answer_fleet_question(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    """Answer a global fleet question using deterministic fleet evidence."""
    normalized = _normalize(question)

    if not normalized:
        return _answer_summary(summary, question)

    if _contains_any(normalized, ["compare", "difference", "similar", "across incidents"]):
        return _answer_compare(summary, question, normalized)

    if _contains_any(normalized, ["worst", "highest priority", "top priority", "inspect first", "critical machine"]):
        return _answer_top_priority(summary, question)

    if _contains_any(normalized, ["line1_motor2", "line2_motor1", "line1_motor1", "line2_motor2", "line3_motor1", "line3_motor2"]):
        return _answer_machine_focus(summary, question, normalized)

    if _contains_any(normalized, ["bearing", "bearing wear", "current anomaly", "fault", "issue", "cause", "causes"]):
        return _answer_fault_patterns(summary, question, normalized)

    if _contains_any(normalized, ["how many", "count", "number of", "incidents", "machines"]):
        return _answer_counts(summary, question)

    if _contains_any(normalized, ["timeline", "when", "time", "sequence"]):
        return _answer_timeline(summary, question)

    if _contains_any(normalized, ["what should", "action", "maintenance", "technician", "recommend"]):
        return _answer_actions(summary, question)

    if _contains_any(normalized, ["summary", "overview", "what happened", "fleet"]):
        return _answer_summary(summary, question)

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_no_result",
        answer=(
            "I could not map that to a fleet-maintenance question. I can compare incidents, "
            "summarize repeated faults, rank machines by priority, list incident counts, "
            "or explain why a machine is high priority."
        ),
        evidence=[],
        suggested_followups=_default_followups(),
    )


def export_global_fleet_analysis(
    summary_path: str | Path,
    output_json_path: str | Path,
    output_markdown_path: str | Path,
) -> dict[str, Any]:
    """Export global fleet fault-pattern analysis."""
    summary = load_fleet_summary(summary_path)
    patterns = analyze_fault_patterns(summary)

    payload = {
        "fleet": summary.get("fleet", {}),
        "fault_patterns": [asdict(pattern) for pattern in patterns],
        "example_questions": _default_followups(),
    }

    output_json = Path(output_json_path)
    output_markdown = Path(output_markdown_path)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_markdown.write_text(_analysis_to_markdown(payload), encoding="utf-8")

    return payload


def _answer_summary(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    fleet = summary.get("fleet", {})
    machines = summary.get("machines", [])
    incidents = summary.get("incidents", [])
    patterns = analyze_fault_patterns(summary)

    top_fault = patterns[0] if patterns else None
    top_machine = _machine_with_most_incidents(machines)

    answer = (
        f"The fleet contains {fleet.get('machine_count', len(machines))} machines, "
        f"{fleet.get('sensor_rows', 0)} sensor rows, and {fleet.get('incident_rows', len(incidents))} incidents "
        f"from {fleet.get('time_start', 'unknown')} to {fleet.get('time_end', 'unknown')}. "
    )
    if top_machine:
        answer += (
            f"The machine with the most incidents is {top_machine['machine_id']} "
            f"with {top_machine['incident_count']} incidents. "
        )
    if top_fault:
        answer += (
            f"The most common suspected fault is {top_fault.suspected_fault} "
            f"with {top_fault.incident_count} incidents."
        )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_summary",
        answer=answer,
        evidence=[
            f"Machines: {fleet.get('machine_count', len(machines))}",
            f"Incidents: {fleet.get('incident_rows', len(incidents))}",
            f"Top repeated fault: {top_fault.suspected_fault if top_fault else 'none'}",
        ],
        suggested_followups=_default_followups(),
    )


def _answer_counts(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    fleet = summary.get("fleet", {})
    patterns = analyze_fault_patterns(summary)
    pattern_text = ", ".join(
        f"{pattern.suspected_fault}: {pattern.incident_count}"
        for pattern in patterns
    )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_counts",
        answer=(
            f"The fleet has {fleet.get('machine_count', 0)} machines and "
            f"{fleet.get('incident_rows', 0)} incidents. Fault counts: {pattern_text}."
        ),
        evidence=[pattern_text],
        suggested_followups=[
            "Compare bearing wear incidents.",
            "Which machine has the most incidents?",
            "Which issue appears most often?",
        ],
    )


def _answer_top_priority(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    machines = summary.get("machines", [])
    if not machines:
        return _no_data_answer(question)

    top_machine = _machine_with_most_risk(machines)
    answer = (
        f"The top maintenance priority is {top_machine['machine_id']} "
        f"({top_machine.get('display_name', top_machine['machine_id'])}). "
        f"It has {top_machine['incident_count']} incidents, minimum health score "
        f"{top_machine['minimum_health_score']}, {top_machine['anomaly_rows']} anomaly rows, "
        f"and suspected faults: {', '.join(top_machine.get('suspected_faults', [])) or 'none'}."
    )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_top_priority",
        answer=answer,
        evidence=[
            f"Machine: {top_machine['machine_id']}",
            f"Incident count: {top_machine['incident_count']}",
            f"Minimum health: {top_machine['minimum_health_score']}",
            f"Anomaly rows: {top_machine['anomaly_rows']}",
        ],
        suggested_followups=[
            f"Why is {top_machine['machine_id']} high priority?",
            "Compare its incidents.",
            "What should the technician inspect first?",
        ],
    )


def _answer_machine_focus(summary: dict[str, Any], question: str, normalized: str) -> FleetQuestionAnswer:
    machine_id = _extract_machine_id(normalized)
    if not machine_id:
        return _answer_top_priority(summary, question)

    machines = {machine["machine_id"]: machine for machine in summary.get("machines", [])}
    machine = machines.get(machine_id)
    if not machine:
        return FleetQuestionAnswer(
            question=question,
            intent="fleet_machine_not_found",
            answer=f"I could not find machine {machine_id} in the fleet summary.",
            evidence=[],
            suggested_followups=_default_followups(),
        )

    incidents = [
        incident for incident in summary.get("incidents", [])
        if incident.get("machine_id") == machine_id
    ]

    incident_bits = [
        f"{incident['incident_id']} ({incident['severity']}, {incident['suspected_fault']})"
        for incident in incidents
    ]

    answer = (
        f"{machine_id} has {machine['incident_count']} incidents, minimum health "
        f"{machine['minimum_health_score']}, {machine['anomaly_rows']} anomaly rows, "
        f"and suspected faults: {', '.join(machine.get('suspected_faults', [])) or 'none'}. "
        f"Incidents: {', '.join(incident_bits) if incident_bits else 'none'}."
    )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_machine_focus",
        answer=answer,
        evidence=incident_bits,
        suggested_followups=[
            f"Compare {machine_id} incidents.",
            f"What should we do for {machine_id}?",
            "Which other machine has similar faults?",
        ],
    )


def _answer_fault_patterns(summary: dict[str, Any], question: str, normalized: str) -> FleetQuestionAnswer:
    patterns = analyze_fault_patterns(summary)
    selected_fault = _extract_fault(normalized)

    if selected_fault:
        patterns = [pattern for pattern in patterns if pattern.suspected_fault == selected_fault]

    if not patterns:
        return FleetQuestionAnswer(
            question=question,
            intent="fleet_fault_not_found",
            answer="No matching fault pattern was found in the fleet incidents.",
            evidence=[],
            suggested_followups=_default_followups(),
        )

    lines = []
    evidence = []
    for pattern in patterns:
        lines.append(
            f"{pattern.suspected_fault}: {pattern.incident_count} incident(s) across "
            f"{', '.join(pattern.machines)}; severity counts {pattern.severity_counts}; "
            f"average duration {pattern.average_duration_seconds}s; max anomaly {pattern.max_anomaly_score}; "
            f"common sensors: {', '.join(pattern.common_sensors)}."
        )
        evidence.append(
            f"{pattern.suspected_fault}: incidents {', '.join(pattern.incident_ids)}"
        )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_fault_patterns",
        answer=" ".join(lines),
        evidence=evidence,
        suggested_followups=[
            "Compare bearing wear incidents.",
            "Which machine should we inspect first?",
            "Show current anomaly incidents.",
        ],
    )


def _answer_compare(summary: dict[str, Any], question: str, normalized: str) -> FleetQuestionAnswer:
    selected_fault = _extract_fault(normalized)
    incidents = summary.get("incidents", [])

    if selected_fault:
        incidents = [
            incident for incident in incidents
            if incident.get("suspected_fault") == selected_fault
        ]

    if not incidents:
        return _no_data_answer(question)

    incidents = sorted(
        incidents,
        key=lambda item: (
            str(item.get("suspected_fault", "")),
            float(item.get("max_anomaly_score", 0.0)),
            int(item.get("duration_seconds", 0)),
        ),
        reverse=True,
    )

    comparison = []
    evidence = []
    for incident in incidents[:8]:
        sensors = ", ".join(incident.get("contributing_sensors", []))
        comparison.append(
            f"{incident['incident_id']} on {incident['machine_id']} was {incident['severity']} "
            f"{incident['suspected_fault']}, lasted {incident['duration_seconds']}s, "
            f"max anomaly {incident['max_anomaly_score']}, sensors: {sensors}."
        )
        evidence.append(
            f"{incident['incident_id']}: {incident['machine_id']}, {incident['severity']}, "
            f"{incident['suspected_fault']}"
        )

    label = selected_fault if selected_fault else "fleet incidents"
    return FleetQuestionAnswer(
        question=question,
        intent="fleet_incident_comparison",
        answer=f"Comparison for {label}: " + " ".join(comparison),
        evidence=evidence,
        suggested_followups=[
            "Which one is highest priority?",
            "Which sensors repeat across these incidents?",
            "What should maintenance inspect first?",
        ],
    )


def _answer_timeline(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    incidents = sorted(summary.get("incidents", []), key=lambda item: item.get("start_time", ""))
    if not incidents:
        return _no_data_answer(question)

    bits = [
        f"{incident['start_time']}: {incident['incident_id']} on {incident['machine_id']} "
        f"({incident['severity']}, {incident['suspected_fault']})"
        for incident in incidents[:12]
    ]
    return FleetQuestionAnswer(
        question=question,
        intent="fleet_timeline",
        answer="Fleet incident timeline: " + " | ".join(bits),
        evidence=bits,
        suggested_followups=[
            "Compare incidents by fault.",
            "Which machine has repeated issues?",
            "Which incident lasted longest?",
        ],
    )


def _answer_actions(summary: dict[str, Any], question: str) -> FleetQuestionAnswer:
    machines = summary.get("machines", [])
    if not machines:
        return _no_data_answer(question)

    top_machine = _machine_with_most_risk(machines)
    faults = set(top_machine.get("suspected_faults", []))

    if "bearing_wear" in faults:
        action = (
            f"Start with {top_machine['machine_id']}: inspect bearings, vibration trend, lubrication, "
            "motor temperature, and current draw. Prioritize this because it has the highest combined "
            "incident/anomaly burden in the fleet."
        )
    elif "current_anomaly" in faults:
        action = (
            f"Start with {top_machine['machine_id']}: inspect electrical current draw, motor load, "
            "drive settings, and power supply stability."
        )
    else:
        action = (
            f"Start with {top_machine['machine_id']}: review its incidents, sensor evidence, "
            "and minimum health score before scheduling maintenance."
        )

    return FleetQuestionAnswer(
        question=question,
        intent="fleet_action",
        answer=action,
        evidence=[
            f"Top machine: {top_machine['machine_id']}",
            f"Incidents: {top_machine['incident_count']}",
            f"Minimum health: {top_machine['minimum_health_score']}",
            f"Faults: {', '.join(top_machine.get('suspected_faults', [])) or 'none'}",
        ],
        suggested_followups=[
            f"Why is {top_machine['machine_id']} the top priority?",
            "Compare its incidents.",
            "Which sensors repeat across incidents?",
        ],
    )


def _analysis_to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# TwinAgent AI Global Fleet Incident Analysis",
        "",
        "## Fleet scope",
        "",
        f"- Machines: {payload['fleet'].get('machine_count')}",
        f"- Sensor rows: {payload['fleet'].get('sensor_rows')}",
        f"- Incidents: {payload['fleet'].get('incident_rows')}",
        "",
        "## Fault patterns",
        "",
        "| Fault | Incidents | Machines | Severity counts | Avg duration | Max anomaly | Common sensors |",
        "|---|---:|---|---|---:|---:|---|",
    ]
    for pattern in payload["fault_patterns"]:
        lines.append(
            "| "
            f"{pattern['suspected_fault']} | "
            f"{pattern['incident_count']} | "
            f"{', '.join(pattern['machines'])} | "
            f"{pattern['severity_counts']} | "
            f"{pattern['average_duration_seconds']} | "
            f"{pattern['max_anomaly_score']} | "
            f"{', '.join(pattern['common_sensors'])} |"
        )

    lines.extend(["", "## Example global questions", ""])
    for question in payload["example_questions"]:
        lines.append(f"- {question}")
    lines.append("")
    return "\n".join(lines)


def _machine_with_most_incidents(machines: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not machines:
        return None
    return max(machines, key=lambda item: (int(item.get("incident_count", 0)), item.get("machine_id", "")))


def _machine_with_most_risk(machines: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        machines,
        key=lambda item: (
            int(item.get("incident_count", 0)) * 40
            + max(0, 100 - int(item.get("minimum_health_score", 100))) * 2
            + int(item.get("anomaly_rows", 0)) / 10,
            item.get("machine_id", ""),
        ),
    )


def _extract_machine_id(text: str) -> str | None:
    match = re.search(r"line\d+_motor\d+", text)
    return match.group(0) if match else None


def _extract_fault(text: str) -> str | None:
    if "bearing" in text:
        return "bearing_wear"
    if "current" in text:
        return "current_anomaly"
    if "overheat" in text:
        return "overheating"
    if "belt" in text:
        return "belt_misalignment"
    return None


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _no_data_answer(question: str) -> FleetQuestionAnswer:
    return FleetQuestionAnswer(
        question=question,
        intent="fleet_no_data",
        answer="No fleet incident data was available for that question.",
        evidence=[],
        suggested_followups=_default_followups(),
    )


def _default_followups() -> list[str]:
    return [
        "Which machine should maintenance inspect first?",
        "Compare bearing wear incidents.",
        "Which issue appears most often?",
        "Show current anomaly incidents.",
    ]
