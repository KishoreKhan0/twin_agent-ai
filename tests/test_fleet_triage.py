"""Tests for TwinAgent AI fleet triage."""

from __future__ import annotations

import json
from pathlib import Path

from twinagent.fleet import build_fleet_triage, export_fleet_triage_report


def _sample_summary() -> dict:
    return {
        "fleet": {
            "machine_count": 2,
            "sensor_rows": 7200,
            "incident_rows": 2,
            "time_start": "2026-05-20T14:00:00",
            "time_end": "2026-05-20T16:00:00",
        },
        "machines": [
            {
                "machine_id": "line1_motor1",
                "line_id": "line1",
                "display_name": "Line 1 Motor 1",
                "rows": 3600,
                "incident_count": 1,
                "latest_health_score": 100,
                "minimum_health_score": 30,
                "latest_risk_level": "healthy",
                "anomaly_rows": 900,
                "suspected_faults": ["bearing_wear"],
            },
            {
                "machine_id": "line1_motor2",
                "line_id": "line1",
                "display_name": "Line 1 Motor 2",
                "rows": 3600,
                "incident_count": 1,
                "latest_health_score": 100,
                "minimum_health_score": 70,
                "latest_risk_level": "healthy",
                "anomaly_rows": 100,
                "suspected_faults": ["current_anomaly"],
            },
        ],
        "incidents": [
            {
                "incident_id": "FLEET-M01-0001",
                "machine_id": "line1_motor1",
                "line_id": "line1",
                "severity": "high",
                "suspected_fault": "bearing_wear",
                "start_time": "2026-05-20T14:10:00",
                "end_time": "2026-05-20T14:30:00",
                "duration_seconds": 1200,
                "max_anomaly_score": 0.75,
                "contributing_sensors": ["temperature_c", "vibration_mm_s", "current_a"],
            },
            {
                "incident_id": "FLEET-M02-0001",
                "machine_id": "line1_motor2",
                "line_id": "line1",
                "severity": "low",
                "suspected_fault": "current_anomaly",
                "start_time": "2026-05-20T15:10:00",
                "end_time": "2026-05-20T15:11:00",
                "duration_seconds": 60,
                "max_anomaly_score": 0.31,
                "contributing_sensors": ["current_a"],
            },
        ],
    }


def test_build_fleet_triage_prioritizes_high_risk_machine() -> None:
    triage = build_fleet_triage(_sample_summary())

    assert triage.fleet_machine_count == 2
    assert triage.fleet_incident_count == 2
    assert triage.top_machine is not None
    assert triage.top_machine.machine_id == "line1_motor1"
    assert triage.top_incident is not None
    assert triage.top_incident.incident_id == "FLEET-M01-0001"
    assert triage.machine_triage[0].priority_score > triage.machine_triage[1].priority_score


def test_export_fleet_triage_report(tmp_path: Path) -> None:
    summary_path = tmp_path / "fleet_summary.json"
    output_json = tmp_path / "fleet_triage.json"
    output_md = tmp_path / "fleet_triage.md"

    summary_path.write_text(json.dumps(_sample_summary()), encoding="utf-8")

    triage = export_fleet_triage_report(
        summary_path=summary_path,
        output_json_path=output_json,
        output_markdown_path=output_md,
    )

    assert triage.top_machine is not None
    assert output_json.exists()
    assert output_md.exists()
    assert "TwinAgent AI Fleet Triage Report" in output_md.read_text(encoding="utf-8")

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["top_machine"]["machine_id"] == "line1_motor1"
