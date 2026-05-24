"""Tests for TwinAgent AI ML feature extraction."""

from __future__ import annotations

import pandas as pd

from twinagent.ml.features import build_window_features, normalize_fault_label


def test_normalize_fault_label_handles_compound_faults() -> None:
    assert normalize_fault_label("normal") == "normal"
    assert normalize_fault_label("bearing_wear+overheating") == "bearing_wear"
    assert normalize_fault_label("overheating+belt_misalignment") == "overheating"
    assert normalize_fault_label(None) == "normal"


def test_build_window_features_creates_labeled_windows() -> None:
    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-05-20T14:00:00", periods=8, freq="s"),
            "machine_id": ["line1_motor1"] * 8,
            "temperature_c": [50, 51, 52, 53, 70, 72, 74, 76],
            "vibration_mm_s": [0.2, 0.2, 0.3, 0.3, 1.1, 1.2, 1.3, 1.4],
            "current_a": [8, 8, 9, 9, 14, 15, 15, 16],
            "fault_label": ["normal", "normal", "normal", "normal", "bearing_wear", "bearing_wear", "bearing_wear", "bearing_wear"],
        }
    )

    features = build_window_features(
        dataframe,
        sensor_columns=["temperature_c", "vibration_mm_s", "current_a"],
        window_size=4,
        step_size=4,
    )

    assert len(features) == 2
    assert "temperature_c_mean" in features.columns
    assert "temperature_c_slope" in features.columns
    assert list(features["target_fault"]) == ["normal", "bearing_wear"]
