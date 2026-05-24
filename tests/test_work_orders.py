"""Tests for maintenance work-order generation."""

from __future__ import annotations

import json
from pathlib import Path

from twinagent.maintenance import build_work_order_queue, export_work_orders


def _sample_incidents() -> list[dict]:
    return [
        {
            "incident_id": "INC-0001",
            "machine_id": "line1_motor1",
            "line_id": "line1",
            "display_name": "Line 1 Motor 1",
            "severity": "high",
            "suspected_fault": "bearing_wear",
            "start_time": "2026-05-20T14:10:00",
            "end_time": "2026-05-20T14:20:00",
            "duration_seconds": 600,
            "max_anomaly_score": 0.83,
            "contributing_sensors": ["temperature_c", "vibration_mm_s", "current_a"],
        },
        {
            "incident_id": "INC-0002",
            "machine_id": "line1_motor1",
            "line_id": "line1",
            "display_name": "Line 1 Motor 1",
            "severity": "medium",
            "suspected_fault": "belt_misalignment",
            "start_time": "2026-05-20T15:10:00",
            "end_time": "2026-05-20T15:14:00",
            "duration_seconds": 240,
            "max_anomaly_score": 0.61,
            "contributing_sensors": ["vibration_mm_s", "throughput_units_min"],
        },
        {
            "incident_id": "INC-0003",
            "machine_id": "line2_motor1",
            "line_id": "line2",
            "display_name": "Line 2 Motor 1",
            "severity": "low",
            "suspected_fault": "current_anomaly",
            "start_time": "2026-05-20T16:10:00",
            "end_time": "2026-05-20T16:11:00",
            "duration_seconds": 60,
            "max_anomaly_score": 0.31,
            "contributing_sensors": ["current_a"],
        },
    ]


def test_build_work_order_queue_prioritizes_high_severity() -> None:
    queue = build_work_order_queue(_sample_incidents(), work_order_prefix="TWO")

    assert queue.total_work_orders == 3
    assert queue.open_p1_count == 1
    assert queue.open_p2_count == 1
    assert queue.machines_affected == 2
    assert queue.work_orders[0].priority == "P1"
    assert queue.work_orders[0].suspected_fault == "bearing_wear"
    assert queue.work_orders[0].inspection_checklist


def test_export_work_orders(tmp_path: Path) -> None:
    incidents_path = tmp_path / "incidents.json"
    output_json = tmp_path / "work_orders.json"
    output_md = tmp_path / "work_orders.md"

    incidents_path.write_text(json.dumps(_sample_incidents()), encoding="utf-8")

    queue = export_work_orders(
        incidents_path=incidents_path,
        output_json_path=output_json,
        output_markdown_path=output_md,
        work_order_prefix="TWO",
    )

    assert queue.total_work_orders == 3
    assert output_json.exists()
    assert output_md.exists()

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["work_orders"][0]["work_order_id"].startswith("TWO-")
    assert "Maintenance Work Orders" in output_md.read_text(encoding="utf-8")
