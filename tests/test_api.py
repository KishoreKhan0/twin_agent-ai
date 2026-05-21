"""Tests for the TwinAgent AI FastAPI backend."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
import yaml

from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.api import create_app
from twinagent.simulation.machine_simulator import MachineSimulator
from twinagent.storage import SQLiteRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepare_api_project(tmp_path: Path) -> Path:
    project_root = tmp_path

    data_processed = project_root / "data" / "processed"
    data_incidents = project_root / "data" / "incidents"
    configs = project_root / "configs"
    knowledge = project_root / "knowledge_base"

    data_processed.mkdir(parents=True)
    data_incidents.mkdir(parents=True)
    configs.mkdir(parents=True)
    knowledge.mkdir(parents=True)

    # The API copilot needs the real knowledge base and RAG config.
    (configs / "rag_config.yaml").write_text(
        (PROJECT_ROOT / "configs" / "rag_config.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    for source in (PROJECT_ROOT / "knowledge_base").glob("*.md"):
        (knowledge / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

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

    processed_path = data_processed / "sensor_data_with_anomalies.csv"
    incidents_path = data_incidents / "incidents.json"
    database_path = data_processed / "twinagent.db"

    processed.to_csv(processed_path, index=False)
    incidents_path.write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    repository = SQLiteRepository(database_path=database_path)
    repository.initialize()
    repository.write_sensor_readings(processed, replace=True)
    repository.write_incidents(incidents, replace=True)

    assert repository.get_sensor_row_count() == 3600
    assert repository.get_incident_count() == 1

    return project_root


def test_api_landing_page(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    response = client.get("/")

    assert response.status_code == 200
    assert "TwinAgent AI" in response.text
    assert "Evidence-grounded maintenance intelligence" in response.text
    assert "/agent/incident-question" in response.text


def test_api_health_endpoint(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["sensor_rows"] == 3600
    assert payload["incident_count"] == 1


def test_api_latest_machine_endpoint(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    response = client.get("/machines/latest?machine_id=line1_motor1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["machine_id"] == "line1_motor1"
    assert payload["health_score"] == 100


def test_api_incident_endpoints(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    list_response = client.get("/incidents")
    detail_response = client.get("/incidents/INC-0001")

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    assert detail_response.status_code == 200
    assert detail_response.json()["incident_id"] == "INC-0001"
    assert detail_response.json()["suspected_fault"] == "bearing_wear"


def test_api_machine_window_endpoint(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    response = client.get(
        "/machines/line1_motor1/window",
        params={
            "start_time": "2026-05-20T14:37:22",
            "end_time": "2026-05-20T14:37:30",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["machine_id"] == "line1_motor1"
    assert payload["rows"] == 5


def test_api_agent_incident_question_endpoint(tmp_path: Path) -> None:
    project_root = _prepare_api_project(tmp_path)
    client = TestClient(create_app(project_root=project_root))

    response = client.post(
        "/agent/incident-question",
        json={
            "incident_id": "INC-0001",
            "question": "Why did this incident trigger?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["incident_id"] == "INC-0001"
    assert "Sensor evidence" in payload["answer"]
    assert "Engineering document guidance" in payload["answer"]
