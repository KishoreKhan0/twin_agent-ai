"""Tests for TwinAgent AI dashboard helper functions."""

from __future__ import annotations

from pathlib import Path

import yaml

from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.dashboard.charts import (
    create_anomaly_score_chart,
    create_health_score_chart,
    create_sensor_timeseries_chart,
)
from twinagent.dashboard.components import (
    build_incident_summary,
    build_machine_overview,
    incidents_to_dataframe,
)
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _processed_and_incidents():
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    health = HealthScoreCalculator()
    processed = health.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    processed = advisor.add_maintenance_columns(processed)

    with (PROJECT_ROOT / "configs" / "anomaly_config.yaml").open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    incidents = IncidentDetector.from_config(config).detect_incidents(processed)
    return processed, incidents


def test_dashboard_overview_has_expected_keys() -> None:
    processed, _ = _processed_and_incidents()

    overview = build_machine_overview(processed)

    assert overview["machine_id"] == "line1_motor1"
    assert overview["total_rows"] == 3600
    assert 0 <= overview["latest_anomaly_score"] <= 1
    assert 5 <= overview["health_score"] <= 100


def test_incident_summary_and_table() -> None:
    _, incidents = _processed_and_incidents()

    summary = build_incident_summary(incidents[0])
    incidents_df = incidents_to_dataframe(incidents)

    assert summary["incident_id"] == "INC-0001"
    assert summary["suspected_fault"]
    assert not incidents_df.empty
    assert "incident_id" in incidents_df.columns


def test_dashboard_sensor_chart_returns_plotly_figure() -> None:
    processed, _ = _processed_and_incidents()

    figure = create_sensor_timeseries_chart(
        processed,
        sensor_columns=["temperature_c", "vibration_mm_s"],
    )

    assert len(figure.data) == 2


def test_dashboard_anomaly_and_health_charts_return_figures() -> None:
    processed, _ = _processed_and_incidents()

    anomaly_figure = create_anomaly_score_chart(processed)
    health_figure = create_health_score_chart(processed)

    assert len(anomaly_figure.data) == 1
    assert len(health_figure.data) == 1
