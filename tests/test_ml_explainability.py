"""Tests for ML explainability and error analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from twinagent.ml import (
    ExplainabilityConfig,
    analyze_prediction_errors,
    export_fault_classifier_explainability,
)
from twinagent.ml.fault_classifier import FaultClassifierConfig, predict_fault_windows, train_fault_classifier


def _sample_training_data() -> pd.DataFrame:
    rows = []
    timestamp = pd.Timestamp("2026-05-20T14:00:00")

    for index in range(300):
        if index < 100:
            label = "normal"
            temp = 50 + (index % 5) * 0.2
            vibration = 0.2 + (index % 3) * 0.01
            current = 8 + (index % 4) * 0.05
        elif index < 200:
            label = "bearing_wear"
            temp = 70 + (index % 5) * 0.4
            vibration = 1.4 + (index % 4) * 0.08
            current = 12 + (index % 4) * 0.2
        else:
            label = "overheating"
            temp = 88 + (index % 5) * 0.5
            vibration = 0.6 + (index % 4) * 0.04
            current = 14 + (index % 4) * 0.3

        rows.append(
            {
                "timestamp": timestamp + pd.Timedelta(seconds=index),
                "machine_id": "line1_motor1",
                "temperature_c": temp,
                "vibration_mm_s": vibration,
                "current_a": current,
                "rpm": 1500,
                "throughput_units_min": 100,
                "fault_label": label,
            }
        )

    return pd.DataFrame(rows)


def test_analyze_prediction_errors_flags_low_confidence() -> None:
    predictions = pd.DataFrame(
        {
            "machine_id": ["m1", "m1", "m1"],
            "target_fault": ["normal", "bearing_wear", "overheating"],
            "predicted_fault": ["normal", "overheating", "overheating"],
            "prediction_confidence": [0.95, 0.41, 0.77],
        }
    )

    error_analysis, audit = analyze_prediction_errors(predictions, low_confidence_threshold=0.6)

    assert error_analysis["window_count"] == 3
    assert error_analysis["low_confidence_count"] == 1
    assert error_analysis["incorrect_count"] == 1
    assert "is_low_confidence" in audit.columns
    assert "is_correct" in audit.columns


def test_export_fault_classifier_explainability(tmp_path: Path) -> None:
    input_path = tmp_path / "training.csv"
    model_path = tmp_path / "fault_classifier.joblib"
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    prediction_path = tmp_path / "predictions.csv"

    feature_importance_path = tmp_path / "feature_importance.csv"
    error_analysis_path = tmp_path / "error_analysis.json"
    model_card_path = tmp_path / "model_card.md"
    audit_path = tmp_path / "audit.csv"

    _sample_training_data().to_csv(input_path, index=False)

    train_fault_classifier(
        input_csv_path=input_path,
        model_path=model_path,
        metrics_path=metrics_path,
        report_path=report_path,
        config=FaultClassifierConfig(window_size=30, step_size=15, n_estimators=25, max_depth=8),
    )

    predict_fault_windows(
        input_csv_path=input_path,
        model_path=model_path,
        output_csv_path=prediction_path,
    )

    result = export_fault_classifier_explainability(
        model_path=model_path,
        metrics_path=metrics_path,
        predictions_path=prediction_path,
        feature_importance_path=feature_importance_path,
        error_analysis_path=error_analysis_path,
        model_card_path=model_card_path,
        audit_csv_path=audit_path,
        config=ExplainabilityConfig(low_confidence_threshold=0.6, top_feature_count=10),
    )

    assert feature_importance_path.exists()
    assert error_analysis_path.exists()
    assert model_card_path.exists()
    assert audit_path.exists()
    assert result.top_feature is not None
    assert "Fault Classifier Model Card" in model_card_path.read_text(encoding="utf-8")

    importance = pd.read_csv(feature_importance_path)
    audit = pd.read_csv(audit_path)

    assert {"rank", "feature", "sensor", "statistic", "importance"}.issubset(importance.columns)
    assert "is_low_confidence" in audit.columns
