"""Tests for ML-assisted incident diagnosis integration."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from twinagent.ml import enrich_incidents_with_ml, export_ml_incident_diagnosis


def _sample_incidents() -> list[dict]:
    return [
        {
            "incident_id": "INC-0001",
            "machine_id": "line1_motor1",
            "severity": "high",
            "suspected_fault": "bearing_wear",
            "start_time": "2026-05-20T14:10:00",
            "end_time": "2026-05-20T14:12:00",
            "duration_seconds": 120,
            "max_anomaly_score": 0.8,
            "contributing_sensors": ["vibration_mm_s"],
        },
        {
            "incident_id": "INC-0002",
            "machine_id": "line1_motor1",
            "severity": "high",
            "suspected_fault": "overheating",
            "start_time": "2026-05-20T14:20:00",
            "end_time": "2026-05-20T14:22:00",
            "duration_seconds": 120,
            "max_anomaly_score": 0.7,
            "contributing_sensors": ["temperature_c"],
        },
    ]


def _sample_predictions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "machine_id": "line1_motor1",
                "window_start_time": "2026-05-20T14:09:30",
                "window_end_time": "2026-05-20T14:10:30",
                "target_fault": "bearing_wear",
                "predicted_fault": "bearing_wear",
                "prediction_confidence": 0.91,
            },
            {
                "machine_id": "line1_motor1",
                "window_start_time": "2026-05-20T14:10:30",
                "window_end_time": "2026-05-20T14:11:30",
                "target_fault": "bearing_wear",
                "predicted_fault": "bearing_wear",
                "prediction_confidence": 0.87,
            },
            {
                "machine_id": "line1_motor1",
                "window_start_time": "2026-05-20T14:19:30",
                "window_end_time": "2026-05-20T14:20:30",
                "target_fault": "overheating",
                "predicted_fault": "cooling_failure",
                "prediction_confidence": 0.72,
            },
        ]
    )


def test_enrich_incidents_with_ml_adds_diagnosis_fields() -> None:
    enriched = enrich_incidents_with_ml(
        _sample_incidents(),
        _sample_predictions(),
        low_confidence_threshold=0.6,
    )

    assert len(enriched) == 2
    assert enriched[0]["ml_predicted_fault"] == "bearing_wear"
    assert enriched[0]["diagnosis_agreement"] is True
    assert enriched[0]["ml_low_confidence"] is False
    assert enriched[0]["ml_matched_window_count"] == 2

    assert enriched[1]["ml_predicted_fault"] == "cooling_failure"
    assert enriched[1]["diagnosis_agreement"] is False
    assert "disagreement" in enriched[1]["ml_diagnosis_note"].lower()


def test_export_ml_incident_diagnosis(tmp_path: Path) -> None:
    incidents_path = tmp_path / "incidents.json"
    predictions_path = tmp_path / "predictions.csv"
    output_json = tmp_path / "incidents_with_ml.json"
    output_md = tmp_path / "ml_incident_report.md"

    incidents_path.write_text(json.dumps(_sample_incidents()), encoding="utf-8")
    _sample_predictions().to_csv(predictions_path, index=False)

    enriched = export_ml_incident_diagnosis(
        incidents_path=incidents_path,
        predictions_path=predictions_path,
        output_json_path=output_json,
        output_markdown_path=output_md,
        low_confidence_threshold=0.6,
    )

    assert output_json.exists()
    assert output_md.exists()
    assert len(enriched) == 2

    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload[0]["ml_predicted_fault"] == "bearing_wear"
    assert "ML-Assisted Incident Diagnosis" in output_md.read_text(encoding="utf-8")
