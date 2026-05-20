"""Evaluation metrics for TwinAgent AI anomaly detection.

The simulator provides ground-truth fault labels, so the anomaly detector can be
evaluated honestly against synthetic fault windows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BinaryDetectionCounts:
    """Confusion-matrix counts for binary anomaly detection."""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def total(self) -> int:
        """Return total number of evaluated rows."""
        return self.true_positive + self.false_positive + self.true_negative + self.false_negative


def compute_binary_detection_metrics(
    dataframe: pd.DataFrame,
    truth_column: str = "fault_label",
    prediction_column: str = "is_anomaly",
) -> dict[str, Any]:
    """Compute point-wise binary anomaly detection metrics."""
    _validate_columns(dataframe, [truth_column, prediction_column])

    truth = dataframe[truth_column].astype(str) != "normal"
    predicted = dataframe[prediction_column].astype(bool)

    counts = BinaryDetectionCounts(
        true_positive=int((truth & predicted).sum()),
        false_positive=int((~truth & predicted).sum()),
        true_negative=int((~truth & ~predicted).sum()),
        false_negative=int((truth & ~predicted).sum()),
    )

    precision = _safe_divide(counts.true_positive, counts.true_positive + counts.false_positive)
    recall = _safe_divide(counts.true_positive, counts.true_positive + counts.false_negative)
    specificity = _safe_divide(counts.true_negative, counts.true_negative + counts.false_positive)
    accuracy = _safe_divide(counts.true_positive + counts.true_negative, counts.total)
    false_positive_rate = _safe_divide(
        counts.false_positive,
        counts.false_positive + counts.true_negative,
    )
    f1_score = _safe_divide(2 * precision * recall, precision + recall)

    return {
        "rows": counts.total,
        "true_positive": counts.true_positive,
        "false_positive": counts.false_positive,
        "true_negative": counts.true_negative,
        "false_negative": counts.false_negative,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "accuracy": round(accuracy, 4),
        "specificity": round(specificity, 4),
        "false_positive_rate": round(false_positive_rate, 4),
    }


def compute_detection_delay(
    dataframe: pd.DataFrame,
    truth_column: str = "fault_label",
    prediction_column: str = "is_anomaly",
    timestamp_column: str = "timestamp",
) -> dict[str, Any]:
    """Compute detection delay for each continuous fault episode."""
    _validate_columns(dataframe, [truth_column, prediction_column, timestamp_column])

    working = dataframe.copy()
    working[timestamp_column] = pd.to_datetime(working[timestamp_column])
    working = working.sort_values(timestamp_column).reset_index(drop=True)

    fault_mask = working[truth_column].astype(str) != "normal"
    episodes = _boolean_runs(fault_mask)

    episode_results: list[dict[str, Any]] = []
    detected_delays: list[float] = []

    for episode_number, (start_index, end_index) in enumerate(episodes, start=1):
        episode = working.iloc[start_index : end_index + 1]
        fault_start = episode[timestamp_column].iloc[0]
        fault_end = episode[timestamp_column].iloc[-1]
        fault_labels = sorted(set(episode[truth_column].astype(str)))

        detected = episode[episode[prediction_column].astype(bool)]
        if detected.empty:
            delay_seconds: float | None = None
            detected_at: str | None = None
        else:
            first_detection = detected[timestamp_column].iloc[0]
            delay_seconds = float((first_detection - fault_start).total_seconds())
            detected_at = first_detection.strftime("%Y-%m-%dT%H:%M:%S")
            detected_delays.append(delay_seconds)

        episode_results.append(
            {
                "episode": episode_number,
                "fault_labels": fault_labels,
                "start_time": fault_start.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": fault_end.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration_seconds": int((fault_end - fault_start).total_seconds()) + 1,
                "detected": delay_seconds is not None,
                "detected_at": detected_at,
                "delay_seconds": delay_seconds,
            }
        )

    return {
        "fault_episodes": len(episode_results),
        "detected_episodes": len(detected_delays),
        "missed_episodes": len(episode_results) - len(detected_delays),
        "mean_detection_delay_seconds": round(sum(detected_delays) / len(detected_delays), 2)
        if detected_delays
        else None,
        "max_detection_delay_seconds": round(max(detected_delays), 2) if detected_delays else None,
        "episodes": episode_results,
    }


def compute_incident_overlap_score(
    dataframe: pd.DataFrame,
    incidents: list[dict[str, Any]],
    truth_column: str = "fault_label",
    timestamp_column: str = "timestamp",
) -> dict[str, Any]:
    """Compute Jaccard overlap between ground-truth fault rows and incident windows."""
    _validate_columns(dataframe, [truth_column, timestamp_column])

    working = dataframe.copy()
    working[timestamp_column] = pd.to_datetime(working[timestamp_column])
    truth = working[truth_column].astype(str) != "normal"

    predicted = pd.Series(False, index=working.index)
    for incident in incidents:
        start = pd.Timestamp(incident["start_time"])
        end = pd.Timestamp(incident["end_time"])
        predicted = predicted | (
            (working[timestamp_column] >= start)
            & (working[timestamp_column] <= end)
        )

    intersection = int((truth & predicted).sum())
    union = int((truth | predicted).sum())
    score = _safe_divide(intersection, union)

    return {
        "incident_count": len(incidents),
        "truth_fault_rows": int(truth.sum()),
        "incident_window_rows": int(predicted.sum()),
        "overlap_rows": intersection,
        "union_rows": union,
        "incident_overlap_score": round(score, 4),
    }


def compute_fault_classification_summary(
    dataframe: pd.DataFrame,
    truth_column: str = "fault_label",
    prediction_column: str = "suspected_fault",
) -> dict[str, Any]:
    """Compute row-level suspected-fault alignment on detected fault rows.

    A row is counted as aligned if the predicted canonical fault is one of the
    active canonical ground-truth faults. This handles overlapping synthetic
    labels such as ``bearing_wear+overheating`` more fairly than forcing a single
    ground-truth class.
    """
    _validate_columns(dataframe, [truth_column, prediction_column, "is_anomaly"])

    working = dataframe.copy()
    working = working[
        (working[truth_column].astype(str) != "normal")
        & (working["is_anomaly"].astype(bool))
    ]

    if working.empty:
        return {
            "evaluated_rows": 0,
            "row_alignment_accuracy": None,
            "accuracy": None,
            "confusion_matrix": [],
        }

    working["truth_fault_types"] = working[truth_column].astype(str).apply(
        lambda value: sorted(_canonical_fault_types(value))
    )
    working["truth_fault_group"] = working["truth_fault_types"].apply("+".join)
    working["predicted_fault_type"] = working[prediction_column].astype(str).apply(
        _canonical_primary_fault_type
    )
    working["is_aligned"] = working.apply(
        lambda row: row["predicted_fault_type"] in set(row["truth_fault_types"]),
        axis=1,
    )

    accuracy = working["is_aligned"].mean()

    confusion = (
        working.groupby(["truth_fault_group", "predicted_fault_type"])
        .size()
        .reset_index(name="count")
        .sort_values(["truth_fault_group", "count"], ascending=[True, False])
    )

    return {
        "evaluated_rows": int(len(working)),
        "row_alignment_accuracy": round(float(accuracy), 4),
        # Keep this alias for compatibility with older output/report code.
        "accuracy": round(float(accuracy), 4),
        "confusion_matrix": confusion.to_dict(orient="records"),
    }


def compute_incident_diagnosis_metrics(
    dataframe: pd.DataFrame,
    incidents: list[dict[str, Any]],
    truth_column: str = "fault_label",
    timestamp_column: str = "timestamp",
) -> dict[str, Any]:
    """Evaluate incident-level suspected-fault diagnosis against overlapping truth.

    This is the most meaningful diagnosis metric for the current MVP because the
    copilot explains incidents, not individual rows.
    """
    _validate_columns(dataframe, [truth_column, timestamp_column])

    working = dataframe.copy()
    working[timestamp_column] = pd.to_datetime(working[timestamp_column])

    diagnosis_rows: list[dict[str, Any]] = []
    correct_count = 0

    for incident in incidents:
        start = pd.Timestamp(incident["start_time"])
        end = pd.Timestamp(incident["end_time"])
        incident_rows = working[
            (working[timestamp_column] >= start)
            & (working[timestamp_column] <= end)
            & (working[truth_column].astype(str) != "normal")
        ]

        truth_faults: set[str] = set()
        for label in incident_rows[truth_column].astype(str):
            truth_faults.update(_canonical_fault_types(label))

        predicted_fault = _canonical_primary_fault_type(str(incident.get("suspected_fault", "")))
        is_correct = predicted_fault in truth_faults if truth_faults else False
        correct_count += int(is_correct)

        diagnosis_rows.append(
            {
                "incident_id": incident.get("incident_id"),
                "predicted_fault": predicted_fault,
                "truth_faults": sorted(truth_faults),
                "is_correct": is_correct,
            }
        )

    accuracy = _safe_divide(correct_count, len(incidents))

    return {
        "evaluated_incidents": len(incidents),
        "correct_incidents": correct_count,
        "incident_diagnosis_accuracy": round(accuracy, 4),
        "diagnoses": diagnosis_rows,
    }


def _canonical_fault_types(value: str) -> set[str]:
    """Map a possibly overlapping label to a set of canonical fault classes."""
    value = value.lower()
    parts = [part.strip() for part in value.split("+") if part.strip()]
    if not parts:
        parts = [value]

    canonical: set[str] = set()
    for part in parts:
        canonical.add(_canonical_primary_fault_type(part))

    return {item for item in canonical if item != "normal"}


def _canonical_primary_fault_type(value: str) -> str:
    """Map a raw or derived fault label to one canonical fault class."""
    value = value.lower()

    if "bearing_wear" in value:
        return "bearing_wear"
    if "belt_misalignment" in value:
        return "belt_misalignment"
    if "overheating" in value or "thermal_anomaly" in value:
        return "overheating"
    if "motor_overload" in value or "current_anomaly" in value:
        return "motor_overload"
    if "vibration_anomaly" in value:
        return "vibration_anomaly"
    if "throughput_anomaly" in value:
        return "throughput_anomaly"
    if "normal" in value:
        return "normal"

    return value or "unknown"


def _boolean_runs(mask: pd.Series) -> list[tuple[int, int]]:
    """Return inclusive start/end indices for True runs in a boolean Series."""
    runs: list[tuple[int, int]] = []
    start_index: int | None = None

    for index, value in enumerate(mask.astype(bool).tolist()):
        if value and start_index is None:
            start_index = index
        elif not value and start_index is not None:
            runs.append((start_index, index - 1))
            start_index = None

    if start_index is not None:
        runs.append((start_index, len(mask) - 1))

    return runs


def _validate_columns(dataframe: pd.DataFrame, columns: list[str]) -> None:
    """Validate that the dataframe contains required columns."""
    if dataframe.empty:
        raise ValueError("Cannot evaluate an empty dataframe.")

    missing = set(columns) - set(dataframe.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))


def _safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, returning 0.0 for zero denominator."""
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)
