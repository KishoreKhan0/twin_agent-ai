"""Tests for TwinAgent AI ML fault classifier."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from twinagent.ml import FaultClassifierConfig, predict_fault_windows, train_fault_classifier


def _sample_training_data() -> pd.DataFrame:
    rows = []
    timestamp = pd.Timestamp("2026-05-20T14:00:00")

    for index in range(240):
        if index < 80:
            label = "normal"
            temp = 50 + (index % 5) * 0.2
            vibration = 0.2 + (index % 3) * 0.01
            current = 8 + (index % 4) * 0.05
        elif index < 160:
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


def test_train_and_predict_fault_classifier(tmp_path: Path) -> None:
    input_path = tmp_path / "training.csv"
    model_path = tmp_path / "fault_classifier.joblib"
    metrics_path = tmp_path / "metrics.json"
    report_path = tmp_path / "report.md"
    prediction_path = tmp_path / "predictions.csv"

    _sample_training_data().to_csv(input_path, index=False)

    result = train_fault_classifier(
        input_csv_path=input_path,
        model_path=model_path,
        metrics_path=metrics_path,
        report_path=report_path,
        config=FaultClassifierConfig(window_size=20, step_size=10, n_estimators=25, max_depth=8),
    )

    assert model_path.exists()
    assert metrics_path.exists()
    assert report_path.exists()
    assert result.window_count > 0
    assert result.class_count >= 3

    predictions = predict_fault_windows(
        input_csv_path=input_path,
        model_path=model_path,
        output_csv_path=prediction_path,
    )

    assert prediction_path.exists()
    assert "predicted_fault" in predictions.columns
    assert "prediction_confidence" in predictions.columns
    assert len(predictions) > 0
