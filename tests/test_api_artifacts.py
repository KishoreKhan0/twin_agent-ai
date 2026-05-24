"""Tests for API artifact endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from twinagent.api.app import create_app


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_api_artifact_endpoints(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "data" / "reports" / "pipeline_run_summary.json",
        {
            "status": "passed",
            "artifact_summary": {
                "local": {"incident_count": 1, "reconciled_incident_count": 1}
            },
        },
    )
    _write_json(
        tmp_path / "data" / "incidents" / "incidents.json",
        [{"incident_id": "INC-0001", "machine_id": "line1_motor1", "suspected_fault": "bearing_wear"}],
    )
    _write_json(
        tmp_path / "data" / "incidents" / "incidents_reconciled.json",
        [
            {
                "incident_id": "INC-0001",
                "machine_id": "line1_motor1",
                "suspected_fault": "vibration_anomaly",
                "final_diagnosis": "bearing_wear",
                "requires_review": False,
            }
        ],
    )
    _write_json(
        tmp_path / "models" / "fault_classifier_metrics.json",
        {
            "window_count": 10,
            "class_count": 3,
            "weighted_f1": 0.9,
        },
    )
    _write_json(
        tmp_path / "data" / "reports" / "local_work_orders.json",
        {
            "total_work_orders": 1,
            "work_orders": [{"work_order_id": "LWO-00001"}],
        },
    )
    _write_json(
        tmp_path / "data" / "fleet" / "reports" / "fleet_summary.json",
        {
            "fleet": {
                "machine_count": 2,
                "incident_rows": 4,
                "sensor_rows": 100,
            }
        },
    )
    _write_json(
        tmp_path / "data" / "fleet" / "reports" / "fleet_triage.json",
        {
            "machines_triaged": 2,
        },
    )
    _write_json(
        tmp_path / "data" / "fleet" / "reports" / "fleet_work_orders.json",
        {
            "total_work_orders": 4,
        },
    )

    app = create_app(project_root=tmp_path)
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    summary = client.get("/summary")
    assert summary.status_code == 200
    assert summary.json()["reconciled_incidents"] == 1
    assert summary.json()["fleet_machines"] == 2
    assert summary.json()["local_work_orders"] == 1

    reconciled = client.get("/incidents/reconciled")
    assert reconciled.status_code == 200
    assert reconciled.json()[0]["final_diagnosis"] == "bearing_wear"

    incident = client.get("/incidents/INC-0001")
    assert incident.status_code == 200
    assert incident.json()["final_diagnosis"] == "bearing_wear"

    ml_metrics = client.get("/ml/metrics")
    assert ml_metrics.status_code == 200
    assert ml_metrics.json()["weighted_f1"] == 0.9

    work_orders = client.get("/work-orders/local")
    assert work_orders.status_code == 200
    assert work_orders.json()["total_work_orders"] == 1

    fleet_summary = client.get("/fleet/summary")
    assert fleet_summary.status_code == 200
    assert fleet_summary.json()["fleet"]["machine_count"] == 2


def test_api_artifact_status_reports_missing_required(tmp_path: Path) -> None:
    app = create_app(project_root=tmp_path)
    client = TestClient(app)

    response = client.get("/artifacts/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "missing_artifacts"
    assert "local_incidents_reconciled" in payload["missing_required"]
