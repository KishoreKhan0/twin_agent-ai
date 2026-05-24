"""Tests for diagnosis reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

from twinagent.ml import (
    DiagnosisReconciliationConfig,
    export_reconciled_incident_diagnoses,
    reconcile_incident_diagnosis,
    reconcile_incident_diagnoses,
)


def test_reconcile_overrides_generic_rule_with_confident_ml() -> None:
    incident = {
        "incident_id": "INC-0001",
        "severity": "medium",
        "suspected_fault": "vibration_anomaly",
        "ml_predicted_fault": "bearing_wear",
        "ml_confidence": 0.96,
        "diagnosis_agreement": False,
        "ml_matched_window_count": 5,
        "ml_prediction_distribution": {"bearing_wear": 5},
    }

    result = reconcile_incident_diagnosis(incident)

    assert result.final_diagnosis == "bearing_wear"
    assert result.final_diagnosis_source == "ml_override_generic_rule"
    assert result.diagnosis_confidence == "high"
    assert result.requires_review is False


def test_reconcile_keeps_rule_when_ml_predicts_normal() -> None:
    incident = {
        "incident_id": "INC-0002",
        "severity": "low",
        "suspected_fault": "throughput_anomaly",
        "ml_predicted_fault": "normal",
        "ml_confidence": 0.99,
        "diagnosis_agreement": False,
        "ml_matched_window_count": 3,
        "ml_prediction_distribution": {"normal": 2, "bearing_wear": 1},
    }

    result = reconcile_incident_diagnosis(incident)

    assert result.final_diagnosis == "throughput_anomaly"
    assert result.final_diagnosis_source == "rule_retained_ml_normal"
    assert result.requires_review is True


def test_reconcile_uses_agreement() -> None:
    incident = {
        "incident_id": "INC-0003",
        "severity": "high",
        "suspected_fault": "bearing_wear",
        "ml_predicted_fault": "bearing_wear",
        "ml_confidence": 0.91,
        "diagnosis_agreement": True,
        "ml_matched_window_count": 4,
        "ml_prediction_distribution": {"bearing_wear": 4},
    }

    result = reconcile_incident_diagnosis(incident)

    assert result.final_diagnosis == "bearing_wear"
    assert result.final_diagnosis_source == "rule_ml_agreement"
    assert result.requires_review is False


def test_reconcile_incident_diagnoses_adds_fields() -> None:
    incidents = [
        {
            "incident_id": "INC-0001",
            "severity": "medium",
            "suspected_fault": "vibration_anomaly",
            "ml_predicted_fault": "bearing_wear",
            "ml_confidence": 0.96,
            "diagnosis_agreement": False,
            "ml_matched_window_count": 5,
            "ml_prediction_distribution": {"bearing_wear": 5},
        }
    ]

    reconciled = reconcile_incident_diagnoses(incidents)

    assert reconciled[0]["final_diagnosis"] == "bearing_wear"
    assert "diagnosis_reason" in reconciled[0]


def test_export_reconciled_incident_diagnoses(tmp_path: Path) -> None:
    input_path = tmp_path / "incidents_with_ml.json"
    output_json = tmp_path / "incidents_reconciled.json"
    output_md = tmp_path / "diagnosis_reconciliation_report.md"

    incidents = [
        {
            "incident_id": "INC-0001",
            "severity": "medium",
            "suspected_fault": "vibration_anomaly",
            "ml_predicted_fault": "bearing_wear",
            "ml_confidence": 0.96,
            "diagnosis_agreement": False,
            "ml_matched_window_count": 5,
            "ml_prediction_distribution": {"bearing_wear": 5},
        }
    ]
    input_path.write_text(json.dumps(incidents), encoding="utf-8")

    reconciled = export_reconciled_incident_diagnoses(
        incidents_with_ml_path=input_path,
        output_json_path=output_json,
        output_markdown_path=output_md,
        config=DiagnosisReconciliationConfig(),
    )

    assert output_json.exists()
    assert output_md.exists()
    assert reconciled[0]["final_diagnosis"] == "bearing_wear"
    assert "Diagnosis Reconciliation Report" in output_md.read_text(encoding="utf-8")
