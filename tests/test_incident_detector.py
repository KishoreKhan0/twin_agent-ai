"""Tests for TwinAgent AI incident detection."""

from __future__ import annotations

from pathlib import Path

import yaml

from twinagent.analytics.anomaly_detection import AnomalyDetector
from twinagent.analytics.incident_detector import IncidentDetector
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _processed_data():
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()
    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    return detector.detect(dataframe)


def test_incident_detector_creates_incidents() -> None:
    processed = _processed_data()

    with (PROJECT_ROOT / "configs" / "anomaly_config.yaml").open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    detector = IncidentDetector.from_config(config)
    incidents = detector.detect_incidents(processed)

    assert len(incidents) >= 1


def test_incident_detector_incident_schema() -> None:
    processed = _processed_data()

    with (PROJECT_ROOT / "configs" / "anomaly_config.yaml").open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    detector = IncidentDetector.from_config(config)
    incidents = detector.detect_incidents(processed)

    first = incidents[0]

    expected_keys = {
        "incident_id",
        "machine_id",
        "start_time",
        "end_time",
        "duration_seconds",
        "severity",
        "suspected_fault",
        "max_anomaly_score",
        "mean_anomaly_score",
        "contributing_sensors",
        "evidence",
    }

    assert expected_keys.issubset(first.keys())
    assert first["incident_id"].startswith("INC-")
    assert first["duration_seconds"] >= 20
    assert first["severity"] in {"low", "medium", "high"}
    assert isinstance(first["contributing_sensors"], list)
    assert isinstance(first["evidence"], dict)
