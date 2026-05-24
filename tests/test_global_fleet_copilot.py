"""Tests for global fleet incident analysis."""

from __future__ import annotations

import json
from pathlib import Path

from twinagent.fleet import (
    analyze_fault_patterns,
    answer_fleet_question,
    export_global_fleet_analysis,
)


def _sample_summary() -> dict:
    return {
        "fleet": {
            "machine_count": 3,
            "sensor_rows": 10800,
            "incident_rows": 4,
            "time_start": "2026-05-20T14:00:00",
            "time_end": "2026-05-20T17:00:00",
        },
        "machines": [
            {
                "machine_id": "line1_motor1",
                "display_name": "Line 1 Motor 1",
                "incident_count": 1,
                "minimum_health_score": 27,
                "anomaly_rows": 900,
                "suspected_faults": ["bearing_wear"],
            },
            {
                "machine_id": "line1_motor2",
                "display_name": "Line 1 Motor 2",
                "incident_count": 2,
                "minimum_health_score": 25,
                "anomaly_rows": 1300,
                "suspected_faults": ["bearing_wear", "current_anomaly"],
            },
            {
                "machine_id": "line2_motor1",
                "display_name": "Line 2 Motor 1",
                "incident_count": 1,
                "minimum_health_score": 31,
                "anomaly_rows": 800,
                "suspected_faults": ["bearing_wear"],
            },
        ],
        "incidents": [
            {
                "incident_id": "FLEET-M01-0001",
                "machine_id": "line1_motor1",
                "severity": "high",
                "suspected_fault": "bearing_wear",
                "start_time": "2026-05-20T14:37:22",
                "end_time": "2026-05-20T14:56:59",
                "duration_seconds": 1178,
                "max_anomaly_score": 0.7526,
                "contributing_sensors": ["current_a", "temperature_c", "vibration_mm_s"],
            },
            {
                "incident_id": "FLEET-M02-0001",
                "machine_id": "line1_motor2",
                "severity": "low",
                "suspected_fault": "current_anomaly",
                "start_time": "2026-05-20T15:14:32",
                "end_time": "2026-05-20T15:14:58",
                "duration_seconds": 27,
                "max_anomaly_score": 0.3091,
                "contributing_sensors": ["current_a"],
            },
            {
                "incident_id": "FLEET-M02-0002",
                "machine_id": "line1_motor2",
                "severity": "high",
                "suspected_fault": "bearing_wear",
                "start_time": "2026-05-20T15:42:44",
                "end_time": "2026-05-20T16:06:59",
                "duration_seconds": 1456,
                "max_anomaly_score": 0.7974,
                "contributing_sensors": ["current_a", "temperature_c", "vibration_mm_s"],
            },
            {
                "incident_id": "FLEET-M03-0001",
                "machine_id": "line2_motor1",
                "severity": "medium",
                "suspected_fault": "bearing_wear",
                "start_time": "2026-05-20T16:59:23",
                "end_time": "2026-05-20T17:08:59",
                "duration_seconds": 577,
                "max_anomaly_score": 0.7001,
                "contributing_sensors": ["temperature_c", "vibration_mm_s"],
            },
        ],
    }


def test_analyze_fault_patterns_groups_incidents() -> None:
    patterns = analyze_fault_patterns(_sample_summary())

    assert patterns[0].suspected_fault == "bearing_wear"
    assert patterns[0].incident_count == 3
    assert "line1_motor2" in patterns[0].machines


def test_answer_fleet_question_compares_bearing_incidents() -> None:
    answer = answer_fleet_question(_sample_summary(), "Compare bearing wear incidents.")

    assert answer.intent == "fleet_incident_comparison"
    assert "FLEET-M02-0002" in answer.answer
    assert "bearing_wear" in answer.answer
    assert answer.suggested_followups


def test_answer_fleet_question_top_priority() -> None:
    answer = answer_fleet_question(_sample_summary(), "Which machine should maintenance inspect first?")

    assert answer.intent == "fleet_top_priority"
    assert "line1_motor2" in answer.answer


def test_export_global_fleet_analysis(tmp_path: Path) -> None:
    summary_path = tmp_path / "fleet_summary.json"
    output_json = tmp_path / "global_fleet_analysis.json"
    output_md = tmp_path / "global_fleet_analysis.md"

    summary_path.write_text(json.dumps(_sample_summary()), encoding="utf-8")

    payload = export_global_fleet_analysis(
        summary_path=summary_path,
        output_json_path=output_json,
        output_markdown_path=output_md,
    )

    assert output_json.exists()
    assert output_md.exists()
    assert payload["fault_patterns"]
    assert "Global Fleet Incident Analysis" in output_md.read_text(encoding="utf-8")
