"""Diagnosis reconciliation for rule-based and ML-assisted incident diagnoses.

The incident detector explains why an anomaly triggered. The ML classifier
predicts the most likely learned fault class from sensor windows. This module
combines both into one final diagnosis field for downstream systems.

It does not hide disagreements. It creates an explicit final diagnosis, source,
confidence level, review flag, and reason.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


GENERIC_RULE_LABELS = {
    "anomaly",
    "unknown",
    "unknown_anomaly",
    "sensor_anomaly",
    "vibration_anomaly",
    "temperature_anomaly",
    "current_anomaly",
    "throughput_anomaly",
    "rpm_anomaly",
    "load_anomaly",
}

ACTIONABLE_FAULTS = {
    "bearing_wear",
    "belt_misalignment",
    "cooling_failure",
    "motor_overload",
    "overheating",
    "sensor_drift",
    "current_anomaly",
}

FAULT_ALIAS = {
    "vibration_anomaly": "bearing_wear",
    "temperature_anomaly": "overheating",
    "throughput_anomaly": "belt_misalignment",
    "current_anomaly": "motor_overload",
}


@dataclass(frozen=True)
class DiagnosisReconciliationConfig:
    """Policy thresholds for diagnosis reconciliation."""

    high_confidence_threshold: float = 0.85
    medium_confidence_threshold: float = 0.65
    low_confidence_threshold: float = 0.60
    require_review_on_disagreement: bool = True


@dataclass(frozen=True)
class DiagnosisReconciliationResult:
    """Final diagnosis decision for one incident."""

    final_diagnosis: str
    final_diagnosis_source: str
    diagnosis_confidence: str
    requires_review: bool
    diagnosis_reason: str


def reconcile_incident_diagnosis(
    incident: dict[str, Any],
    *,
    config: DiagnosisReconciliationConfig | None = None,
) -> DiagnosisReconciliationResult:
    """Reconcile one incident's rule diagnosis and ML diagnosis."""
    cfg = config or DiagnosisReconciliationConfig()

    rule_fault = _clean_fault(incident.get("suspected_fault")) or "unknown_anomaly"
    ml_fault = _clean_fault(incident.get("ml_predicted_fault"))
    ml_confidence = _safe_float(incident.get("ml_confidence"))
    agreement = incident.get("diagnosis_agreement")
    matched_windows = int(incident.get("ml_matched_window_count") or 0)
    distribution = incident.get("ml_prediction_distribution") or {}
    severity = str(incident.get("severity", "unknown")).lower()

    if ml_fault is None or matched_windows == 0:
        final = _alias_or_rule(rule_fault)
        return DiagnosisReconciliationResult(
            final_diagnosis=final,
            final_diagnosis_source="rule_only",
            diagnosis_confidence=_rule_only_confidence(rule_fault, severity),
            requires_review=rule_fault in GENERIC_RULE_LABELS,
            diagnosis_reason=(
                f"No usable ML diagnosis was available. Final diagnosis uses rule label "
                f"`{rule_fault}` mapped to `{final}`."
            ),
        )

    ml_confidence_level = _confidence_level(
        ml_confidence,
        high_threshold=cfg.high_confidence_threshold,
        medium_threshold=cfg.medium_confidence_threshold,
    )

    if agreement is True or rule_fault == ml_fault:
        return DiagnosisReconciliationResult(
            final_diagnosis=ml_fault,
            final_diagnosis_source="rule_ml_agreement",
            diagnosis_confidence=ml_confidence_level,
            requires_review=ml_confidence < cfg.low_confidence_threshold,
            diagnosis_reason=(
                f"Rule diagnosis and ML diagnosis agree on `{ml_fault}`. "
                f"ML confidence is {ml_confidence:.2f} across {matched_windows} matched window(s)."
            ),
        )

    if _is_generic_rule(rule_fault) and _is_actionable_ml(ml_fault) and ml_confidence >= cfg.medium_confidence_threshold:
        return DiagnosisReconciliationResult(
            final_diagnosis=ml_fault,
            final_diagnosis_source="ml_override_generic_rule",
            diagnosis_confidence=ml_confidence_level,
            requires_review=False,
            diagnosis_reason=(
                f"Rule label `{rule_fault}` is generic, while ML predicts actionable fault "
                f"`{ml_fault}` with confidence {ml_confidence:.2f} across {matched_windows} "
                f"matched window(s). Final diagnosis uses ML."
            ),
        )

    if _alias_or_rule(rule_fault) == ml_fault and ml_confidence >= cfg.low_confidence_threshold:
        return DiagnosisReconciliationResult(
            final_diagnosis=ml_fault,
            final_diagnosis_source="ml_confirms_rule_alias",
            diagnosis_confidence=ml_confidence_level,
            requires_review=False,
            diagnosis_reason=(
                f"Rule label `{rule_fault}` maps to `{ml_fault}`, and ML predicts `{ml_fault}` "
                f"with confidence {ml_confidence:.2f}. Final diagnosis uses the mapped fault."
            ),
        )

    if ml_fault == "normal":
        return DiagnosisReconciliationResult(
            final_diagnosis=rule_fault,
            final_diagnosis_source="rule_retained_ml_normal",
            diagnosis_confidence=_combined_disagreement_confidence(rule_fault, ml_confidence),
            requires_review=True,
            diagnosis_reason=(
                f"Rule diagnosis is `{rule_fault}`, but ML predicts normal with confidence "
                f"{ml_confidence:.2f}. Final diagnosis keeps the rule label and flags review."
            ),
        )

    if ml_confidence >= cfg.high_confidence_threshold and _dominant_prediction_share(distribution, ml_fault) >= 0.70:
        return DiagnosisReconciliationResult(
            final_diagnosis=ml_fault,
            final_diagnosis_source="ml_high_confidence_disagreement",
            diagnosis_confidence=ml_confidence_level,
            requires_review=cfg.require_review_on_disagreement,
            diagnosis_reason=(
                f"Rule diagnosis is `{rule_fault}`, while ML predicts `{ml_fault}` with high "
                f"confidence {ml_confidence:.2f} and dominant matched-window support. "
                f"Final diagnosis uses ML but flags disagreement review."
            ),
        )

    return DiagnosisReconciliationResult(
        final_diagnosis=rule_fault,
        final_diagnosis_source="rule_retained_ml_disagreement",
        diagnosis_confidence=_combined_disagreement_confidence(rule_fault, ml_confidence),
        requires_review=True,
        diagnosis_reason=(
            f"Rule diagnosis is `{rule_fault}`, while ML predicts `{ml_fault}` with confidence "
            f"{ml_confidence:.2f}. The disagreement is not strong enough for automatic override, "
            f"so final diagnosis keeps the rule label and requires review."
        ),
    )


def reconcile_incident_diagnoses(
    incidents: list[dict[str, Any]],
    *,
    config: DiagnosisReconciliationConfig | None = None,
) -> list[dict[str, Any]]:
    """Return incidents with final diagnosis fields added."""
    cfg = config or DiagnosisReconciliationConfig()
    reconciled: list[dict[str, Any]] = []

    for incident in incidents:
        decision = reconcile_incident_diagnosis(incident, config=cfg)
        updated = dict(incident)
        updated.update(asdict(decision))
        reconciled.append(updated)

    return reconciled


def export_reconciled_incident_diagnoses(
    *,
    incidents_with_ml_path: str | Path,
    output_json_path: str | Path,
    output_markdown_path: str | Path,
    config: DiagnosisReconciliationConfig | None = None,
) -> list[dict[str, Any]]:
    """Read ML-enriched incidents, reconcile diagnosis, and export reports."""
    input_path = Path(incidents_with_ml_path)
    incidents = json.loads(input_path.read_text(encoding="utf-8"))
    reconciled = reconcile_incident_diagnoses(incidents, config=config)

    output_json = Path(output_json_path)
    output_markdown = Path(output_markdown_path)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(reconciled, indent=2), encoding="utf-8")
    output_markdown.write_text(reconciled_diagnoses_to_markdown(reconciled), encoding="utf-8")

    return reconciled


def reconciled_diagnoses_to_markdown(incidents: list[dict[str, Any]]) -> str:
    """Convert reconciled incidents to Markdown."""
    source_counts = Counter(str(incident.get("final_diagnosis_source", "unknown")) for incident in incidents)
    diagnosis_counts = Counter(str(incident.get("final_diagnosis", "unknown")) for incident in incidents)
    review_count = sum(1 for incident in incidents if incident.get("requires_review") is True)

    lines = [
        "# TwinAgent AI Diagnosis Reconciliation Report",
        "",
        "## Summary",
        "",
        f"- Incidents reconciled: {len(incidents)}",
        f"- Incidents requiring review: {review_count}",
        "",
        "## Final diagnosis counts",
        "",
    ]

    for diagnosis, count in diagnosis_counts.most_common():
        lines.append(f"- `{diagnosis}`: {count}")

    lines.extend(["", "## Decision source counts", ""])
    for source, count in source_counts.most_common():
        lines.append(f"- `{source}`: {count}")

    lines.extend(
        [
            "",
            "## Reconciled incident table",
            "",
            "| Incident | Rule | ML | Final | Source | Confidence | Review |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    for incident in incidents:
        lines.append(
            "| "
            f"{incident.get('incident_id', '')} | "
            f"{incident.get('suspected_fault', '')} | "
            f"{incident.get('ml_predicted_fault') or 'none'} | "
            f"{incident.get('final_diagnosis', '')} | "
            f"{incident.get('final_diagnosis_source', '')} | "
            f"{incident.get('diagnosis_confidence', '')} | "
            f"{incident.get('requires_review')} |"
        )

    lines.extend(["", "## Decision notes", ""])
    for incident in incidents:
        lines.append(
            "- "
            f"`{incident.get('incident_id', '')}`: {incident.get('diagnosis_reason', '')}"
        )

    lines.append("")
    return "\\n".join(lines)


def _clean_fault(value: object) -> str | None:
    """Clean a fault label."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "null"}:
        return None
    return text


def _safe_float(value: object) -> float:
    """Safely parse float."""
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _is_generic_rule(rule_fault: str) -> bool:
    """Return whether a rule label is generic/non-actionable."""
    return rule_fault in GENERIC_RULE_LABELS


def _is_actionable_ml(ml_fault: str) -> bool:
    """Return whether ML label is actionable."""
    return ml_fault in ACTIONABLE_FAULTS


def _alias_or_rule(rule_fault: str) -> str:
    """Map generic rule labels to likely actionable aliases when possible."""
    return FAULT_ALIAS.get(rule_fault, rule_fault)


def _confidence_level(
    value: float,
    *,
    high_threshold: float,
    medium_threshold: float,
) -> str:
    """Convert numeric confidence to label."""
    if value >= high_threshold:
        return "high"
    if value >= medium_threshold:
        return "medium"
    return "low"


def _rule_only_confidence(rule_fault: str, severity: str) -> str:
    """Estimate confidence when only rule diagnosis exists."""
    if rule_fault in GENERIC_RULE_LABELS:
        return "low"
    if severity in {"high", "critical"}:
        return "medium"
    return "low"


def _combined_disagreement_confidence(rule_fault: str, ml_confidence: float) -> str:
    """Conservative confidence for unresolved disagreements."""
    if rule_fault in GENERIC_RULE_LABELS:
        return "low"
    if ml_confidence >= 0.85:
        return "medium"
    return "low"


def _dominant_prediction_share(distribution: dict[str, Any], selected_fault: str) -> float:
    """Return share of selected fault in matched-window prediction distribution."""
    if not distribution:
        return 0.0
    counts = {str(key): int(value) for key, value in distribution.items()}
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return counts.get(selected_fault, 0) / total
