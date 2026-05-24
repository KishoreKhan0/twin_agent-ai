"""ML-assisted incident diagnosis integration.

This module connects the trained fault classifier back into the incident
workflow. It matches ML prediction windows to incident time windows and adds
diagnosis fields to each incident record.

It does not replace the rule-based incident diagnosis. It adds a second opinion.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class IncidentMLDiagnosis:
    """ML diagnosis summary for one incident."""

    incident_id: str
    rule_suspected_fault: str
    ml_predicted_fault: str | None
    ml_confidence: float | None
    diagnosis_agreement: bool | None
    low_confidence: bool
    matched_window_count: int
    matched_window_start: str | None
    matched_window_end: str | None
    prediction_distribution: dict[str, int]
    diagnosis_note: str


def enrich_incidents_with_ml(
    incidents: list[dict[str, Any]],
    predictions: pd.DataFrame,
    *,
    low_confidence_threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """Return incidents enriched with ML-assisted diagnosis fields."""
    if predictions.empty:
        return [
            _merge_incident_with_diagnosis(
                incident,
                _empty_diagnosis(incident, "No ML prediction windows were available."),
            )
            for incident in incidents
        ]

    prepared_predictions = _prepare_predictions(predictions)
    enriched: list[dict[str, Any]] = []

    for incident in incidents:
        matched = _matching_windows(incident, prepared_predictions)
        diagnosis = diagnose_incident_with_windows(
            incident=incident,
            matched_windows=matched,
            low_confidence_threshold=low_confidence_threshold,
        )
        enriched.append(_merge_incident_with_diagnosis(incident, diagnosis))

    return enriched


def export_ml_incident_diagnosis(
    *,
    incidents_path: str | Path,
    predictions_path: str | Path,
    output_json_path: str | Path,
    output_markdown_path: str | Path,
    low_confidence_threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """Read incidents/predictions, enrich incidents, and export JSON + Markdown."""
    incidents = json.loads(Path(incidents_path).read_text(encoding="utf-8"))
    predictions = pd.read_csv(predictions_path)

    enriched = enrich_incidents_with_ml(
        incidents,
        predictions,
        low_confidence_threshold=low_confidence_threshold,
    )

    output_json = Path(output_json_path)
    output_markdown = Path(output_markdown_path)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    output_markdown.write_text(ml_incident_diagnosis_to_markdown(enriched), encoding="utf-8")

    return enriched


def diagnose_incident_with_windows(
    *,
    incident: dict[str, Any],
    matched_windows: pd.DataFrame,
    low_confidence_threshold: float,
) -> IncidentMLDiagnosis:
    """Create diagnosis object for one incident using matched ML windows."""
    rule_fault = str(incident.get("suspected_fault", "unknown_anomaly"))

    if matched_windows.empty:
        return _empty_diagnosis(
            incident,
            "No ML prediction windows overlapped this incident time window.",
        )

    predicted_faults = matched_windows["predicted_fault"].astype(str)
    confidences = pd.to_numeric(
        matched_windows["prediction_confidence"],
        errors="coerce",
    ).fillna(0.0)

    weighted_scores: dict[str, float] = defaultdict(float)
    for fault, confidence in zip(predicted_faults, confidences):
        weighted_scores[str(fault)] += float(confidence)

    ml_fault = max(weighted_scores, key=lambda fault: (weighted_scores[fault], fault))
    ml_fault_rows = matched_windows[predicted_faults == ml_fault]
    ml_confidence = round(
        float(pd.to_numeric(ml_fault_rows["prediction_confidence"], errors="coerce").fillna(0.0).mean()),
        4,
    )

    agreement = rule_fault == ml_fault
    low_confidence = ml_confidence < low_confidence_threshold

    distribution = dict(Counter(predicted_faults))
    note = _diagnosis_note(
        rule_fault=rule_fault,
        ml_fault=ml_fault,
        ml_confidence=ml_confidence,
        agreement=agreement,
        low_confidence=low_confidence,
        matched_count=len(matched_windows),
    )

    return IncidentMLDiagnosis(
        incident_id=str(incident.get("incident_id", "")),
        rule_suspected_fault=rule_fault,
        ml_predicted_fault=ml_fault,
        ml_confidence=ml_confidence,
        diagnosis_agreement=agreement,
        low_confidence=low_confidence,
        matched_window_count=int(len(matched_windows)),
        matched_window_start=_timestamp_or_none(matched_windows["window_start_time"].min()),
        matched_window_end=_timestamp_or_none(matched_windows["window_end_time"].max()),
        prediction_distribution=distribution,
        diagnosis_note=note,
    )


def ml_incident_diagnosis_to_markdown(enriched_incidents: list[dict[str, Any]]) -> str:
    """Convert enriched incident records to Markdown report."""
    total = len(enriched_incidents)
    with_ml = [item for item in enriched_incidents if item.get("ml_predicted_fault")]
    disagreements = [item for item in with_ml if item.get("diagnosis_agreement") is False]
    low_confidence = [item for item in with_ml if item.get("ml_low_confidence") is True]

    lines = [
        "# TwinAgent AI ML-Assisted Incident Diagnosis",
        "",
        "## Summary",
        "",
        f"- Incidents analyzed: {total}",
        f"- Incidents with ML windows: {len(with_ml)}",
        f"- Rule/ML disagreements: {len(disagreements)}",
        f"- Low-confidence ML diagnoses: {len(low_confidence)}",
        "",
        "## Incident diagnosis table",
        "",
        "| Incident | Rule fault | ML fault | Confidence | Agreement | Low confidence | Matched windows |",
        "|---|---|---|---:|---|---|---:|",
    ]

    for incident in enriched_incidents:
        lines.append(
            "| "
            f"{incident.get('incident_id', '')} | "
            f"{incident.get('suspected_fault', '')} | "
            f"{incident.get('ml_predicted_fault') or 'none'} | "
            f"{incident.get('ml_confidence') if incident.get('ml_confidence') is not None else 'n/a'} | "
            f"{incident.get('diagnosis_agreement') if incident.get('diagnosis_agreement') is not None else 'n/a'} | "
            f"{incident.get('ml_low_confidence')} | "
            f"{incident.get('ml_matched_window_count', 0)} |"
        )

    lines.extend(["", "## Review notes", ""])

    for incident in enriched_incidents:
        lines.append(
            "- "
            f"`{incident.get('incident_id', '')}`: {incident.get('ml_diagnosis_note', '')}"
        )

    lines.append("")
    return "\n".join(lines)


def _prepare_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    """Validate and prepare prediction dataframe."""
    required = {
        "machine_id",
        "window_start_time",
        "window_end_time",
        "predicted_fault",
        "prediction_confidence",
    }
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"Prediction data is missing required columns: {sorted(missing)}")

    prepared = predictions.copy()
    prepared["window_start_time"] = pd.to_datetime(prepared["window_start_time"])
    prepared["window_end_time"] = pd.to_datetime(prepared["window_end_time"])
    prepared["prediction_confidence"] = pd.to_numeric(
        prepared["prediction_confidence"],
        errors="coerce",
    ).fillna(0.0)
    return prepared


def _matching_windows(incident: dict[str, Any], predictions: pd.DataFrame) -> pd.DataFrame:
    """Return ML prediction windows overlapping an incident."""
    machine_id = str(incident.get("machine_id", ""))
    incident_start = pd.Timestamp(incident["start_time"])
    incident_end = pd.Timestamp(incident["end_time"])

    same_machine = predictions["machine_id"].astype(str) == machine_id
    overlaps = (
        (predictions["window_end_time"] >= incident_start)
        & (predictions["window_start_time"] <= incident_end)
    )

    return predictions[same_machine & overlaps].copy()


def _empty_diagnosis(incident: dict[str, Any], note: str) -> IncidentMLDiagnosis:
    """Return empty diagnosis object for an incident."""
    return IncidentMLDiagnosis(
        incident_id=str(incident.get("incident_id", "")),
        rule_suspected_fault=str(incident.get("suspected_fault", "unknown_anomaly")),
        ml_predicted_fault=None,
        ml_confidence=None,
        diagnosis_agreement=None,
        low_confidence=True,
        matched_window_count=0,
        matched_window_start=None,
        matched_window_end=None,
        prediction_distribution={},
        diagnosis_note=note,
    )


def _merge_incident_with_diagnosis(
    incident: dict[str, Any],
    diagnosis: IncidentMLDiagnosis,
) -> dict[str, Any]:
    """Merge diagnosis fields into incident record."""
    updated = dict(incident)
    payload = asdict(diagnosis)
    updated.update(
        {
            "ml_predicted_fault": payload["ml_predicted_fault"],
            "ml_confidence": payload["ml_confidence"],
            "diagnosis_agreement": payload["diagnosis_agreement"],
            "ml_low_confidence": payload["low_confidence"],
            "ml_matched_window_count": payload["matched_window_count"],
            "ml_matched_window_start": payload["matched_window_start"],
            "ml_matched_window_end": payload["matched_window_end"],
            "ml_prediction_distribution": payload["prediction_distribution"],
            "ml_diagnosis_note": payload["diagnosis_note"],
        }
    )
    return updated


def _diagnosis_note(
    *,
    rule_fault: str,
    ml_fault: str,
    ml_confidence: float,
    agreement: bool,
    low_confidence: bool,
    matched_count: int,
) -> str:
    """Return human-readable diagnosis note."""
    confidence_text = f"{ml_confidence:.2f}"
    if agreement and not low_confidence:
        return (
            f"Rule diagnosis and ML diagnosis agree on {rule_fault}. "
            f"ML confidence is {confidence_text} across {matched_count} matched window(s)."
        )

    if agreement and low_confidence:
        return (
            f"Rule diagnosis and ML diagnosis agree on {rule_fault}, but ML confidence "
            f"is low ({confidence_text}). Review sensor evidence before relying on the prediction."
        )

    if not agreement and low_confidence:
        return (
            f"Rule diagnosis is {rule_fault}, while ML predicts {ml_fault} with low confidence "
            f"({confidence_text}). Treat this as an ambiguous incident and review overlapping symptoms."
        )

    return (
        f"Rule diagnosis is {rule_fault}, while ML predicts {ml_fault} with confidence "
        f"{confidence_text}. Review disagreement and compare contributing sensors."
    )


def _timestamp_or_none(value: object) -> str | None:
    """Return timestamp string or None."""
    if pd.isna(value):
        return None
    return str(value)
