"""Tests for TwinAgent AI SQLite storage layer."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation.machine_simulator import MachineSimulator
from twinagent.storage import SQLiteRepository, initialize_database


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


def test_initialize_database_creates_file(tmp_path: Path) -> None:
    database_path = tmp_path / "twinagent.db"

    returned_path = initialize_database(database_path)

    assert returned_path.exists()
    assert returned_path == database_path


def test_repository_writes_and_counts_rows(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()
    repository = SQLiteRepository(database_path=tmp_path / "twinagent.db")

    sensor_count = repository.write_sensor_readings(processed)
    incident_count = repository.write_incidents(incidents)

    assert sensor_count == 3600
    assert incident_count >= 1
    assert repository.get_sensor_row_count() == 3600
    assert repository.get_incident_count() == len(incidents)


def test_repository_get_latest_machine_state(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()
    repository = SQLiteRepository(database_path=tmp_path / "twinagent.db")
    repository.write_sensor_readings(processed)
    repository.write_incidents(incidents)

    latest = repository.get_latest_machine_state("line1_motor1")

    assert latest["machine_id"] == "line1_motor1"
    assert latest["timestamp"] == "2026-05-20T14:59:59"
    assert "health_score" in latest
    assert "risk_level" in latest


def test_repository_query_sensor_window(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()
    repository = SQLiteRepository(database_path=tmp_path / "twinagent.db")
    repository.write_sensor_readings(processed)
    repository.write_incidents(incidents)

    incident = repository.get_incident("INC-0001")
    window = repository.query_sensor_window(
        machine_id=incident["machine_id"],
        start_time=incident["start_time"],
        end_time=incident["end_time"],
    )

    assert not window.empty
    assert window["machine_id"].nunique() == 1
    assert window["machine_id"].iloc[0] == "line1_motor1"


def test_repository_round_trips_incident_json_fields(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()
    repository = SQLiteRepository(database_path=tmp_path / "twinagent.db")
    repository.write_sensor_readings(processed)
    repository.write_incidents(incidents)

    incident = repository.get_incident("INC-0001")

    assert incident["incident_id"] == "INC-0001"
    assert isinstance(incident["contributing_sensors"], list)
    assert isinstance(incident["evidence"], dict)
    assert incident["suspected_fault"] == "bearing_wear"


def test_repository_clear_all(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()
    repository = SQLiteRepository(database_path=tmp_path / "twinagent.db")
    repository.write_sensor_readings(processed)
    repository.write_incidents(incidents)

    repository.clear_all()

    assert repository.get_sensor_row_count() == 0
    assert repository.get_incident_count() == 0
