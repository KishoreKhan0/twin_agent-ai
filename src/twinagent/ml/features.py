"""Feature engineering for TwinAgent AI fault diagnosis.

The ML classifier works on time-series windows instead of individual rows.
Each window is converted into statistical features such as mean, max, std,
range, and slope for each available sensor.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_SENSOR_COLUMNS = [
    "temperature_c",
    "vibration_mm_s",
    "rpm",
    "current_a",
    "load_pct",
    "belt_speed_mps",
    "throughput_units_min",
    "ambient_temperature_c",
    "anomaly_score",
    "health_score",
]

FAULT_PRIORITY = [
    "bearing_wear",
    "overheating",
    "belt_misalignment",
    "motor_overload",
    "cooling_failure",
    "sensor_drift",
    "current_anomaly",
    "unknown_anomaly",
]


def normalize_fault_label(label: object) -> str:
    """Convert raw simulator fault labels into a single ML target label.

    The simulator may produce compound labels such as
    ``bearing_wear+overheating``. For a simple first ML classifier, we map each
    window to one primary fault label using a deterministic priority list.
    """
    if label is None:
        return "normal"

    text = str(label).strip()
    if not text or text.lower() in {"nan", "none", "normal"}:
        return "normal"

    parts = [part.strip() for part in text.split("+") if part.strip()]
    if not parts:
        return "normal"

    for fault in FAULT_PRIORITY:
        if fault in parts:
            return fault

    return parts[0]


def build_window_features(
    dataframe: pd.DataFrame,
    *,
    sensor_columns: Iterable[str] | None = None,
    window_size: int = 120,
    step_size: int = 60,
    label_column: str = "fault_label",
    timestamp_column: str = "timestamp",
    machine_id_column: str = "machine_id",
    include_labels: bool = True,
) -> pd.DataFrame:
    """Build window-level features from a sensor dataframe.

    Parameters
    ----------
    dataframe:
        Input sensor dataframe. It can be raw or processed.
    sensor_columns:
        Candidate numeric columns to use. Missing columns are ignored.
    window_size:
        Number of rows per feature window.
    step_size:
        Number of rows between consecutive windows.
    include_labels:
        If true and ``label_column`` exists, add a ``target_fault`` column.
    """
    if dataframe.empty:
        return pd.DataFrame()

    if window_size <= 1:
        raise ValueError("window_size must be greater than 1.")
    if step_size <= 0:
        raise ValueError("step_size must be positive.")

    data = dataframe.copy()
    if timestamp_column in data.columns:
        data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        data = data.sort_values([machine_id_column, timestamp_column] if machine_id_column in data.columns else [timestamp_column])

    columns = list(sensor_columns or DEFAULT_SENSOR_COLUMNS)
    usable_columns = [
        column
        for column in columns
        if column in data.columns and pd.api.types.is_numeric_dtype(data[column])
    ]
    if not usable_columns:
        raise ValueError("No usable numeric sensor columns were found for feature extraction.")

    group_keys = [machine_id_column] if machine_id_column in data.columns else [None]
    rows: list[dict[str, object]] = []

    if group_keys == [None]:
        groups = [("unknown", data)]
    else:
        groups = list(data.groupby(machine_id_column, sort=True))

    for machine_id, group in groups:
        group = group.reset_index(drop=True)
        if len(group) < window_size:
            continue

        for start_index in range(0, len(group) - window_size + 1, step_size):
            window = group.iloc[start_index:start_index + window_size]
            row = _window_to_feature_row(
                window=window,
                usable_columns=usable_columns,
                machine_id=str(machine_id),
                start_index=start_index,
                timestamp_column=timestamp_column,
            )

            if include_labels and label_column in window.columns:
                row["target_fault"] = _window_target_label(window[label_column])

            rows.append(row)

    features = pd.DataFrame(rows)
    if not features.empty and "target_fault" in features.columns:
        non_feature_columns = {
            "machine_id",
            "window_start_index",
            "window_start_time",
            "window_end_time",
            "target_fault",
        }
        feature_columns = [column for column in features.columns if column not in non_feature_columns]
        features = features[
            ["machine_id", "window_start_index", "window_start_time", "window_end_time"]
            + feature_columns
            + ["target_fault"]
        ]

    return features


def _window_to_feature_row(
    *,
    window: pd.DataFrame,
    usable_columns: list[str],
    machine_id: str,
    start_index: int,
    timestamp_column: str,
) -> dict[str, object]:
    """Convert one window to one feature row."""
    row: dict[str, object] = {
        "machine_id": machine_id,
        "window_start_index": int(start_index),
    }

    if timestamp_column in window.columns:
        row["window_start_time"] = str(window[timestamp_column].iloc[0])
        row["window_end_time"] = str(window[timestamp_column].iloc[-1])
    else:
        row["window_start_time"] = ""
        row["window_end_time"] = ""

    for column in usable_columns:
        values = pd.to_numeric(window[column], errors="coerce").dropna()
        if values.empty:
            continue

        row[f"{column}_mean"] = float(values.mean())
        row[f"{column}_std"] = float(values.std(ddof=0))
        row[f"{column}_min"] = float(values.min())
        row[f"{column}_max"] = float(values.max())
        row[f"{column}_range"] = float(values.max() - values.min())
        row[f"{column}_last"] = float(values.iloc[-1])
        row[f"{column}_slope"] = _safe_slope(values.to_numpy(dtype=float))

    return row


def _window_target_label(labels: pd.Series) -> str:
    """Return primary target label for a window."""
    normalized = [normalize_fault_label(label) for label in labels]
    non_normal = [label for label in normalized if label != "normal"]

    if not non_normal:
        return "normal"

    counts = Counter(non_normal)
    return sorted(counts.items(), key=lambda item: (-item[1], FAULT_PRIORITY.index(item[0]) if item[0] in FAULT_PRIORITY else 999))[0][0]


def _safe_slope(values: np.ndarray) -> float:
    """Return linear slope for a numeric sequence."""
    if len(values) < 2:
        return 0.0

    x_values = np.arange(len(values), dtype=float)
    if np.allclose(values, values[0]):
        return 0.0

    slope, _ = np.polyfit(x_values, values, deg=1)
    if not np.isfinite(slope):
        return 0.0
    return float(slope)
