"""Tests for TwinAgent AI fleet dashboard helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from twinagent.dashboard.fleet_components import (
    FleetDashboardPaths,
    build_fleet_overview,
    fleet_artifacts_available,
    fleet_incidents_table,
    fleet_machine_table,
    filter_fleet_machine,
    incidents_for_machine,
    load_fleet_incidents,
    load_fleet_processed_data,
    load_fleet_summary,
)


def _write_fleet_fixture(tmp_path: Path) -> FleetDashboardPaths:
    paths = FleetDashboardPaths(project_root=tmp_path)
    paths.processed_data_path.parent.mkdir(parents=True)
    paths.incidents_path.parent.mkdir(parents=True)
    paths.summary_path.parent.mkdir(parents=True)

    dataframe = pd.DataFrame(
        [
            {
                "timestamp": "2026-05-20T14:00:00",
                "machine_id": "line1_motor1",
                "temperature_c": 50.0,
                "vibration_mm_s": 1.0,
                "current_a": 8.5,
                "health_score": 100,
                "risk_level": "healthy",
                "anomaly_score": 0.0,
            },
            {
                "timestamp": "2026-05-20T14:00:01",
                "machine_id": "line1_motor2",
                "temperature_c": 70.0,
                "vibration_mm_s": 2.0,
                "current_a": 14.0,
                "health_score": 40,
                "risk_level": "high",
                "anomaly_score": 0.7,
            },
        ]
    )
    dataframe.to_csv(paths.processed_data_path, index=False)

    incidents = [
        {
            "incident_id": "FLEET-M02-0001",
            "machine_id": "line1_motor2",
            "line_id": "line1",
            "severity": "high",
            "suspected_fault": "bearing_wear",
            "start_time": "2026-05-20T14:00:01",
            "end_time": "2026-05-20T14:00:05",
            "duration_seconds": 5,
            "max_anomaly_score": 0.7,
            "contributing_sensors": ["temperature_c"],
        }
    ]
    paths.incidents_path.write_text(json.dumps(incidents), encoding="utf-8")

    summary = {
        "fleet": {
            "machine_count": 2,
            "sensor_rows": 2,
            "incident_rows": 1,
            "time_start": "2026-05-20T14:00:00",
            "time_end": "2026-05-20T14:00:05",
        },
        "machines": [
            {
                "machine_id": "line1_motor1",
                "line_id": "line1",
                "display_name": "Line 1 Motor 1",
                "rows": 1,
                "incident_count": 0,
                "latest_timestamp": "2026-05-20T14:00:00",
                "latest_health_score": 100,
                "minimum_health_score": 100,
                "latest_risk_level": "healthy",
                "anomaly_rows": 0,
                "suspected_faults": [],
            },
            {
                "machine_id": "line1_motor2",
                "line_id": "line1",
                "display_name": "Line 1 Motor 2",
                "rows": 1,
                "incident_count": 1,
                "latest_timestamp": "2026-05-20T14:00:01",
                "latest_health_score": 40,
                "minimum_health_score": 40,
                "latest_risk_level": "high",
                "anomaly_rows": 1,
                "suspected_faults": ["bearing_wear"],
            },
        ],
        "incidents": incidents,
    }
    paths.summary_path.write_text(json.dumps(summary), encoding="utf-8")

    return paths


def test_fleet_dashboard_helpers_load_and_summarize(tmp_path: Path) -> None:
    paths = _write_fleet_fixture(tmp_path)

    assert fleet_artifacts_available(paths)

    dataframe = load_fleet_processed_data(paths.processed_data_path)
    incidents = load_fleet_incidents(paths.incidents_path)
    summary = load_fleet_summary(paths.summary_path)

    overview = build_fleet_overview(summary)
    machine_table = fleet_machine_table(summary)
    incidents_table = fleet_incidents_table(incidents)

    assert len(dataframe) == 2
    assert overview["machine_count"] == 2
    assert overview["incident_rows"] == 1
    assert overview["worst_machine_id"] == "line1_motor2"
    assert list(machine_table["machine_id"]) == ["line1_motor1", "line1_motor2"]
    assert incidents_table.iloc[0]["incident_id"] == "FLEET-M02-0001"


def test_fleet_dashboard_filters_machine_data(tmp_path: Path) -> None:
    paths = _write_fleet_fixture(tmp_path)
    dataframe = load_fleet_processed_data(paths.processed_data_path)
    incidents = load_fleet_incidents(paths.incidents_path)

    machine_frame = filter_fleet_machine(dataframe, "line1_motor2")
    machine_incidents = incidents_for_machine(incidents, "line1_motor2")

    assert len(machine_frame) == 1
    assert machine_frame.iloc[0]["machine_id"] == "line1_motor2"
    assert len(machine_incidents) == 1
