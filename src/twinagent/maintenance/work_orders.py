"""Maintenance work-order generation for TwinAgent AI.

This module converts local or fleet incident data into actionable maintenance
work orders. It is deterministic and designed for dashboards, reports, and API
exposure later.

If an incident contains reconciled diagnosis fields, work orders use
``final_diagnosis`` as the technician-facing fault while preserving the original
rule/ML diagnosis in the evidence summary.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


FAULT_CHECKLISTS = {
    "bearing_wear": [
        "Inspect bearing housing for abnormal vibration and heat.",
        "Check lubrication condition and contamination.",
        "Review vibration trend around the incident window.",
        "Inspect shaft alignment and coupling condition.",
        "Plan bearing replacement if vibration remains elevated.",
    ],
    "overheating": [
        "Check cooling airflow and fan operation.",
        "Inspect motor surface temperature and thermal hot spots.",
        "Verify motor load and duty cycle during the incident.",
        "Inspect electrical terminals for loose or heated contacts.",
        "Confirm ambient temperature and ventilation conditions.",
    ],
    "cooling_failure": [
        "Inspect cooling fan, airflow path, and heat exchanger surfaces.",
        "Check for blocked vents or dust buildup.",
        "Verify ambient temperature and cooling response after load changes.",
        "Inspect temperature trend against motor current and load.",
        "Run controlled cooldown check before returning to full duty.",
    ],
    "motor_overload": [
        "Inspect motor current draw under production load.",
        "Check conveyor for mechanical jam, drag, or overloading.",
        "Review drive/VFD overload history and current limits.",
        "Verify belt tension and downstream blockage.",
        "Reduce load and retest current stability.",
    ],
    "belt_misalignment": [
        "Inspect belt tracking and pulley alignment.",
        "Check belt tension and edge wear.",
        "Inspect idlers/rollers for seizure or uneven rotation.",
        "Verify conveyor load distribution.",
        "Realign belt before restarting at full load.",
    ],
    "current_anomaly": [
        "Inspect motor current draw under load.",
        "Check drive/VFD settings and overload history.",
        "Verify power supply stability and phase imbalance.",
        "Inspect mechanical load for jam or drag.",
        "Compare current trend against vibration and temperature.",
    ],
    "sensor_drift": [
        "Validate sensor calibration against a trusted reference.",
        "Inspect sensor wiring, mounting, and environmental exposure.",
        "Compare reading trend against neighboring sensors.",
        "Check whether drift persists after restart/recalibration.",
        "Replace sensor if drift remains unexplained.",
    ],
    "unknown_anomaly": [
        "Review contributing sensor traces.",
        "Inspect machine condition near the incident time window.",
        "Check for simultaneous load, temperature, and vibration excursions.",
        "Escalate to reliability engineer if repeated.",
    ],
}

FAULT_ACTIONS = {
    "bearing_wear": "Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.",
    "overheating": "Inspect cooling path, motor load, ambient conditions, and electrical terminals before extended operation.",
    "cooling_failure": "Inspect cooling system health, airflow, fan condition, and thermal recovery before returning to full duty.",
    "motor_overload": "Inspect electrical current draw, mechanical loading, conveyor drag, and drive/VFD overload history.",
    "belt_misalignment": "Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.",
    "current_anomaly": "Inspect electrical current draw, drive/VFD parameters, power supply quality, and mechanical load.",
    "sensor_drift": "Validate sensor calibration and wiring before using the sensor for maintenance decisions.",
    "unknown_anomaly": "Review sensor evidence and perform general mechanical/electrical inspection.",
}

SEVERITY_PRIORITY = {
    "critical": "P1",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
    "none": "P4",
}

PRIORITY_DUE_HOURS = {
    "P1": 4,
    "P2": 24,
    "P3": 72,
    "P4": 168,
}


@dataclass(frozen=True)
class WorkOrder:
    """Actionable maintenance work order."""

    work_order_id: str
    source_incident_id: str
    machine_id: str
    line_id: str
    display_name: str
    priority: str
    severity: str
    suspected_fault: str
    status: str
    start_time: str
    end_time: str
    due_within_hours: int
    estimated_effort_minutes: int
    recommended_action: str
    inspection_checklist: list[str]
    safety_note: str
    evidence_summary: str
    contributing_sensors: list[str]


@dataclass(frozen=True)
class WorkOrderQueue:
    """Collection of work orders and summary metrics."""

    total_work_orders: int
    open_p1_count: int
    open_p2_count: int
    machines_affected: int
    top_priority_machine: str | None
    work_orders: list[WorkOrder]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable queue."""
        return {
            "total_work_orders": self.total_work_orders,
            "open_p1_count": self.open_p1_count,
            "open_p2_count": self.open_p2_count,
            "machines_affected": self.machines_affected,
            "top_priority_machine": self.top_priority_machine,
            "work_orders": [asdict(order) for order in self.work_orders],
        }


def build_work_order_queue(
    incidents: list[dict[str, Any]],
    *,
    work_order_prefix: str = "WO",
) -> WorkOrderQueue:
    """Build a prioritized work-order queue from incident dictionaries."""
    orders = [
        _incident_to_work_order(incident=incident, index=index, prefix=work_order_prefix)
        for index, incident in enumerate(incidents, start=1)
    ]
    orders = sorted(
        orders,
        key=lambda order: (
            _priority_rank(order.priority),
            order.start_time,
            order.machine_id,
            order.work_order_id,
        ),
    )

    machine_priority_counts: dict[str, int] = {}
    for order in orders:
        if order.priority in {"P1", "P2"}:
            machine_priority_counts[order.machine_id] = machine_priority_counts.get(order.machine_id, 0) + 1

    top_machine = None
    if machine_priority_counts:
        top_machine = max(
            machine_priority_counts,
            key=lambda machine: (machine_priority_counts[machine], machine),
        )

    return WorkOrderQueue(
        total_work_orders=len(orders),
        open_p1_count=sum(1 for order in orders if order.priority == "P1"),
        open_p2_count=sum(1 for order in orders if order.priority == "P2"),
        machines_affected=len({order.machine_id for order in orders}),
        top_priority_machine=top_machine,
        work_orders=orders,
    )


def export_work_orders(
    incidents_path: str | Path,
    output_json_path: str | Path,
    output_markdown_path: str | Path,
    *,
    work_order_prefix: str = "WO",
) -> WorkOrderQueue:
    """Load incidents and export work-order queue JSON + Markdown."""
    incidents_file = Path(incidents_path)
    incidents = json.loads(incidents_file.read_text(encoding="utf-8"))

    queue = build_work_order_queue(incidents, work_order_prefix=work_order_prefix)

    output_json = Path(output_json_path)
    output_markdown = Path(output_markdown_path)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(queue.to_dict(), indent=2), encoding="utf-8")
    output_markdown.write_text(work_orders_to_markdown(queue), encoding="utf-8")

    return queue


def work_orders_to_markdown(queue: WorkOrderQueue) -> str:
    """Convert work-order queue to Markdown."""
    lines = [
        "# TwinAgent AI Maintenance Work Orders",
        "",
        "## Queue summary",
        "",
        f"- Total work orders: {queue.total_work_orders}",
        f"- Open P1: {queue.open_p1_count}",
        f"- Open P2: {queue.open_p2_count}",
        f"- Machines affected: {queue.machines_affected}",
        f"- Top priority machine: `{queue.top_priority_machine or 'none'}`",
        "",
        "## Work-order queue",
        "",
        "| Work order | Incident | Machine | Priority | Severity | Fault | Due | Effort |",
        "|---|---|---|---|---|---|---:|---:|",
    ]

    for order in queue.work_orders:
        lines.append(
            "| "
            f"{order.work_order_id} | "
            f"{order.source_incident_id} | "
            f"{order.machine_id} | "
            f"{order.priority} | "
            f"{order.severity} | "
            f"{order.suspected_fault} | "
            f"{order.due_within_hours}h | "
            f"{order.estimated_effort_minutes}m |"
        )

    lines.extend(["", "## Detailed instructions", ""])

    for order in queue.work_orders:
        lines.extend(
            [
                f"### {order.work_order_id} — {order.machine_id}",
                "",
                f"- Incident: `{order.source_incident_id}`",
                f"- Priority: **{order.priority}**",
                f"- Severity: **{order.severity}**",
                f"- Fault: **{order.suspected_fault}**",
                f"- Time window: `{order.start_time}` → `{order.end_time}`",
                f"- Due within: **{order.due_within_hours} hours**",
                f"- Estimated effort: **{order.estimated_effort_minutes} minutes**",
                f"- Recommended action: {order.recommended_action}",
                f"- Evidence: {order.evidence_summary}",
                f"- Safety note: {order.safety_note}",
                "",
                "Checklist:",
            ]
        )
        for item in order.inspection_checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")

    return "\n".join(lines)


def _incident_to_work_order(
    incident: dict[str, Any],
    index: int,
    prefix: str,
) -> WorkOrder:
    """Convert one incident to a work order."""
    severity = str(incident.get("severity", "none")).lower()
    fault = str(incident.get("final_diagnosis") or incident.get("suspected_fault") or "unknown_anomaly")
    priority = SEVERITY_PRIORITY.get(severity, "P3")
    duration = int(incident.get("duration_seconds", 0))
    max_anomaly = float(incident.get("max_anomaly_score", 0.0))
    sensors = list(incident.get("contributing_sensors", []))

    effort = _estimated_effort_minutes(
        priority=priority,
        fault=fault,
        duration_seconds=duration,
        sensor_count=len(sensors),
    )

    evidence = _evidence_summary(
        incident=incident,
        fault=fault,
        severity=severity,
        duration=duration,
        max_anomaly=max_anomaly,
        sensors=sensors,
    )

    return WorkOrder(
        work_order_id=f"{prefix}-{index:05d}",
        source_incident_id=str(incident.get("incident_id", "")),
        machine_id=str(incident.get("machine_id", "")),
        line_id=str(incident.get("line_id", "unknown")),
        display_name=str(incident.get("display_name", incident.get("machine_id", ""))),
        priority=priority,
        severity=severity,
        suspected_fault=fault,
        status="open",
        start_time=str(incident.get("start_time", "")),
        end_time=str(incident.get("end_time", "")),
        due_within_hours=PRIORITY_DUE_HOURS.get(priority, 72),
        estimated_effort_minutes=effort,
        recommended_action=FAULT_ACTIONS.get(fault, FAULT_ACTIONS["unknown_anomaly"]),
        inspection_checklist=FAULT_CHECKLISTS.get(fault, FAULT_CHECKLISTS["unknown_anomaly"]),
        safety_note=_safety_note(priority=priority, fault=fault),
        evidence_summary=evidence,
        contributing_sensors=sensors,
    )


def _evidence_summary(
    *,
    incident: dict[str, Any],
    fault: str,
    severity: str,
    duration: int,
    max_anomaly: float,
    sensors: list[str],
) -> str:
    """Build evidence summary for a work order."""
    base = (
        f"{severity} incident with final diagnosis {fault}; duration {duration}s; "
        f"max anomaly {round(max_anomaly, 4)}; sensors: {', '.join(sensors) or 'none'}."
    )

    if "final_diagnosis_source" in incident:
        base += (
            f" Diagnosis source: {incident.get('final_diagnosis_source')}; "
            f"rule={incident.get('suspected_fault')}; "
            f"ml={incident.get('ml_predicted_fault')} "
            f"({incident.get('ml_confidence')})."
        )

    if incident.get("requires_review") is True:
        base += " Diagnosis requires review before closing the work order."

    return base


def _priority_rank(priority: str) -> int:
    """Sort rank for priority."""
    return {"P1": 0, "P2": 1, "P3": 2, "P4": 3}.get(priority, 9)


def _estimated_effort_minutes(
    *,
    priority: str,
    fault: str,
    duration_seconds: int,
    sensor_count: int,
) -> int:
    """Estimate technician effort."""
    base = {"P1": 90, "P2": 60, "P3": 35, "P4": 20}.get(priority, 35)
    if fault in {"bearing_wear", "belt_misalignment"}:
        base += 30
    elif fault in {"overheating", "current_anomaly", "cooling_failure", "motor_overload"}:
        base += 20
    elif fault == "sensor_drift":
        base += 15

    base += min(duration_seconds // 300 * 10, 40)
    base += min(sensor_count * 5, 20)
    return int(base)


def _safety_note(*, priority: str, fault: str) -> str:
    """Return safety note for work order."""
    if priority == "P1":
        return "Treat as urgent. Lock out/tag out before physical inspection if machine intervention is required."
    if fault in {"current_anomaly", "overheating", "cooling_failure", "motor_overload"}:
        return "Verify electrical and thermal safety before touching motor housing or terminals."
    return "Follow standard maintenance safety procedure before inspection."
