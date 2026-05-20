"""Tests for TwinAgent AI health-score logic."""

from __future__ import annotations

from pathlib import Path

from twinagent.analytics.anomaly_detection import AnomalyDetector
from twinagent.analytics.health_score import HealthScoreCalculator
from twinagent.analytics.predictive_maintenance import PredictiveMaintenanceAdvisor
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _processed_with_health():
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    health_calculator = HealthScoreCalculator()
    processed = health_calculator.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    return advisor.add_maintenance_columns(processed)


def test_health_score_columns_are_added() -> None:
    processed = _processed_with_health()

    assert "health_score" in processed.columns
    assert "risk_level" in processed.columns
    assert "maintenance_urgency" in processed.columns
    assert "maintenance_recommendation" in processed.columns


def test_health_score_range_is_valid() -> None:
    processed = _processed_with_health()

    assert processed["health_score"].between(5, 100).all()


def test_fault_rows_have_lower_average_health_than_normal_rows() -> None:
    processed = _processed_with_health()

    normal_rows = processed[processed["fault_label"] == "normal"]
    fault_rows = processed[processed["fault_label"] != "normal"]

    assert fault_rows["health_score"].mean() < normal_rows["health_score"].mean()


def test_anomalies_receive_non_normal_maintenance_urgency() -> None:
    processed = _processed_with_health()

    anomaly_rows = processed[processed["is_anomaly"]]

    assert not anomaly_rows.empty
    assert (anomaly_rows["maintenance_urgency"] != "normal_operation").any()


def test_maintenance_recommendation_is_human_readable() -> None:
    processed = _processed_with_health()

    recommendations = processed["maintenance_recommendation"].dropna().astype(str)

    assert recommendations.str.len().min() > 10
    assert recommendations.str.contains("Inspect|Check|Continue|Review", regex=True).any()
