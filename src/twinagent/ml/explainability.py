"""ML explainability and error analysis for TwinAgent AI.

This module turns a trained fault classifier into useful engineering artifacts:

- feature importance table
- prediction audit CSV
- error-analysis JSON
- model card Markdown

It intentionally avoids dashboards and keeps the ML layer auditable from files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


@dataclass(frozen=True)
class ExplainabilityConfig:
    """Configuration for model explainability export."""

    low_confidence_threshold: float = 0.6
    weak_class_f1_threshold: float = 0.7
    low_support_threshold: int = 5
    top_feature_count: int = 25


@dataclass(frozen=True)
class ExplainabilityResult:
    """Paths and compact summary from explainability export."""

    feature_importance_path: str
    error_analysis_path: str
    model_card_path: str
    audit_csv_path: str
    top_feature: str | None
    low_confidence_count: int
    incorrect_count: int | None
    weak_classes: list[str]


def export_fault_classifier_explainability(
    *,
    model_path: str | Path,
    metrics_path: str | Path,
    predictions_path: str | Path,
    feature_importance_path: str | Path,
    error_analysis_path: str | Path,
    model_card_path: str | Path,
    audit_csv_path: str | Path,
    config: ExplainabilityConfig | None = None,
) -> ExplainabilityResult:
    """Export feature importance, error analysis, model card, and audit CSV."""
    cfg = config or ExplainabilityConfig()

    artifact = joblib.load(Path(model_path))
    metrics = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
    predictions = pd.read_csv(predictions_path)

    feature_importance = extract_feature_importance(artifact)
    error_analysis, audit = analyze_prediction_errors(
        predictions,
        low_confidence_threshold=cfg.low_confidence_threshold,
    )
    weak_classes = identify_weak_classes(
        metrics=metrics,
        f1_threshold=cfg.weak_class_f1_threshold,
        support_threshold=cfg.low_support_threshold,
    )

    feature_importance_output = Path(feature_importance_path)
    error_analysis_output = Path(error_analysis_path)
    model_card_output = Path(model_card_path)
    audit_output = Path(audit_csv_path)

    for path in [feature_importance_output, error_analysis_output, model_card_output, audit_output]:
        path.parent.mkdir(parents=True, exist_ok=True)

    feature_importance.to_csv(feature_importance_output, index=False)
    error_analysis_output.write_text(json.dumps(error_analysis, indent=2), encoding="utf-8")
    audit.to_csv(audit_output, index=False)

    model_card = build_model_card(
        metrics=metrics,
        feature_importance=feature_importance,
        error_analysis=error_analysis,
        weak_classes=weak_classes,
        config=cfg,
    )
    model_card_output.write_text(model_card, encoding="utf-8")

    top_feature = None
    if not feature_importance.empty:
        top_feature = str(feature_importance.iloc[0]["feature"])

    return ExplainabilityResult(
        feature_importance_path=str(feature_importance_output),
        error_analysis_path=str(error_analysis_output),
        model_card_path=str(model_card_output),
        audit_csv_path=str(audit_output),
        top_feature=top_feature,
        low_confidence_count=int(error_analysis["low_confidence_count"]),
        incorrect_count=error_analysis.get("incorrect_count"),
        weak_classes=weak_classes,
    )


def extract_feature_importance(artifact: dict[str, Any]) -> pd.DataFrame:
    """Extract feature importances from a saved model artifact."""
    model = artifact.get("model")
    feature_columns = list(artifact.get("feature_columns", []))

    if model is None:
        raise ValueError("Model artifact is missing the model object.")
    if not feature_columns:
        raise ValueError("Model artifact is missing feature columns.")

    classifier = model
    if hasattr(model, "named_steps"):
        classifier = model.named_steps.get("classifier", model)

    if not hasattr(classifier, "feature_importances_"):
        raise ValueError("Classifier does not expose feature_importances_.")

    importances = list(classifier.feature_importances_)
    if len(importances) != len(feature_columns):
        raise ValueError("Feature importance length does not match feature columns.")

    rows = []
    for feature, importance in zip(feature_columns, importances):
        sensor, statistic = split_feature_name(feature)
        rows.append(
            {
                "feature": feature,
                "sensor": sensor,
                "statistic": statistic,
                "importance": round(float(importance), 8),
            }
        )

    dataframe = pd.DataFrame(rows).sort_values("importance", ascending=False).reset_index(drop=True)
    dataframe.insert(0, "rank", range(1, len(dataframe) + 1))
    return dataframe


def analyze_prediction_errors(
    predictions: pd.DataFrame,
    *,
    low_confidence_threshold: float = 0.6,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Analyze window-level prediction errors and low-confidence predictions."""
    required = {"predicted_fault", "prediction_confidence"}
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"Prediction data is missing required columns: {sorted(missing)}")

    audit = predictions.copy()
    audit["prediction_confidence"] = pd.to_numeric(
        audit["prediction_confidence"],
        errors="coerce",
    ).fillna(0.0)
    audit["is_low_confidence"] = audit["prediction_confidence"] < low_confidence_threshold

    has_target = "target_fault" in audit.columns
    if has_target:
        audit["is_correct"] = audit["target_fault"].astype(str) == audit["predicted_fault"].astype(str)
    else:
        audit["is_correct"] = pd.NA

    low_confidence = audit[audit["is_low_confidence"]]
    error_analysis: dict[str, Any] = {
        "window_count": int(len(audit)),
        "low_confidence_threshold": low_confidence_threshold,
        "low_confidence_count": int(len(low_confidence)),
        "low_confidence_rate": round(float(len(low_confidence) / len(audit)), 4) if len(audit) else 0.0,
        "predicted_fault_counts": audit["predicted_fault"].value_counts().to_dict(),
        "low_confidence_fault_counts": low_confidence["predicted_fault"].value_counts().to_dict(),
    }

    if has_target:
        incorrect = audit[audit["is_correct"] == False]  # noqa: E712
        error_analysis.update(
            {
                "incorrect_count": int(len(incorrect)),
                "error_rate": round(float(len(incorrect) / len(audit)), 4) if len(audit) else 0.0,
                "target_fault_counts": audit["target_fault"].value_counts().to_dict(),
                "incorrect_by_target": incorrect["target_fault"].value_counts().to_dict(),
                "confusion_pairs": _confusion_pairs(incorrect),
            }
        )

    ordered_columns = [
        column
        for column in [
            "machine_id",
            "window_start_index",
            "window_start_time",
            "window_end_time",
            "target_fault",
            "predicted_fault",
            "prediction_confidence",
            "is_correct",
            "is_low_confidence",
        ]
        if column in audit.columns
    ]
    other_columns = [column for column in audit.columns if column not in ordered_columns and not column.startswith("prob_")]
    probability_columns = [column for column in audit.columns if column.startswith("prob_")]
    audit = audit[ordered_columns + other_columns + probability_columns]

    return error_analysis, audit


def identify_weak_classes(
    *,
    metrics: dict[str, Any],
    f1_threshold: float,
    support_threshold: int,
) -> list[str]:
    """Return classes that have weak F1 or very low support."""
    report = metrics.get("classification_report", {})
    classes = metrics.get("classes", [])
    weak: list[str] = []

    for class_name in classes:
        class_report = report.get(class_name, {})
        f1_value = float(class_report.get("f1-score", 0.0))
        support = int(class_report.get("support", 0))
        if f1_value < f1_threshold or support <= support_threshold:
            weak.append(str(class_name))

    return weak


def build_model_card(
    *,
    metrics: dict[str, Any],
    feature_importance: pd.DataFrame,
    error_analysis: dict[str, Any],
    weak_classes: list[str],
    config: ExplainabilityConfig,
) -> str:
    """Build a concise Markdown model card."""
    lines = [
        "# TwinAgent AI Fault Classifier Model Card",
        "",
        "## Purpose",
        "",
        "This model predicts the dominant fault type from rolling windows of simulated industrial sensor data.",
        "",
        "## Training summary",
        "",
        f"- Windows: {metrics.get('window_count')}",
        f"- Train windows: {metrics.get('train_window_count')}",
        f"- Test windows: {metrics.get('test_window_count')}",
        f"- Feature count: {metrics.get('feature_count')}",
        f"- Classes: {metrics.get('class_count')}",
        f"- Accuracy: {metrics.get('accuracy')}",
        f"- Macro F1: {metrics.get('macro_f1')}",
        f"- Weighted F1: {metrics.get('weighted_f1')}",
        "",
        "## Weak classes to monitor",
        "",
    ]

    if weak_classes:
        for class_name in weak_classes:
            class_report = metrics.get("classification_report", {}).get(class_name, {})
            lines.append(
                f"- `{class_name}` — F1 `{round(float(class_report.get('f1-score', 0.0)), 4)}`, "
                f"support `{int(class_report.get('support', 0))}`"
            )
    else:
        lines.append("- None under the configured thresholds.")

    lines.extend(
        [
            "",
            "## Top feature importances",
            "",
            "| Rank | Feature | Sensor | Statistic | Importance |",
            "|---:|---|---|---|---:|",
        ]
    )

    for _, row in feature_importance.head(config.top_feature_count).iterrows():
        lines.append(
            "| "
            f"{int(row['rank'])} | "
            f"{row['feature']} | "
            f"{row['sensor']} | "
            f"{row['statistic']} | "
            f"{row['importance']} |"
        )

    lines.extend(
        [
            "",
            "## Prediction audit summary",
            "",
            f"- Prediction windows: {error_analysis.get('window_count')}",
            f"- Low-confidence threshold: {error_analysis.get('low_confidence_threshold')}",
            f"- Low-confidence windows: {error_analysis.get('low_confidence_count')}",
            f"- Low-confidence rate: {error_analysis.get('low_confidence_rate')}",
        ]
    )

    if "incorrect_count" in error_analysis:
        lines.extend(
            [
                f"- Incorrect windows: {error_analysis.get('incorrect_count')}",
                f"- Error rate: {error_analysis.get('error_rate')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The model is trained on synthetic data, not certified production data.",
            "- Weak classes with low support should not be overclaimed.",
            "- Predictions should support, not replace, technician inspection decisions.",
            "- Data drift should be monitored before using the model on new machines or real assets.",
            "",
        ]
    )

    return "\n".join(lines)


def split_feature_name(feature: str) -> tuple[str, str]:
    """Split feature names like temperature_c_mean into sensor/statistic."""
    suffixes = ["_mean", "_std", "_min", "_max", "_range", "_last", "_slope"]
    for suffix in suffixes:
        if feature.endswith(suffix):
            return feature[: -len(suffix)], suffix[1:]
    return feature, "unknown"


def _confusion_pairs(incorrect: pd.DataFrame) -> list[dict[str, Any]]:
    """Return compact target/predicted confusion-pair counts."""
    if incorrect.empty:
        return []

    pairs = (
        incorrect.groupby(["target_fault", "predicted_fault"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return [
        {
            "target_fault": str(row["target_fault"]),
            "predicted_fault": str(row["predicted_fault"]),
            "count": int(row["count"]),
        }
        for _, row in pairs.iterrows()
    ]
