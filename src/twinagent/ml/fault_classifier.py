"""ML fault classifier for TwinAgent AI.

This module trains and runs a supervised classifier over time-window features.
It intentionally stays lightweight and uses scikit-learn so it can run locally
without cloud services.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from twinagent.ml.features import build_window_features


NON_FEATURE_COLUMNS = {
    "machine_id",
    "window_start_index",
    "window_start_time",
    "window_end_time",
    "target_fault",
}


@dataclass(frozen=True)
class FaultClassifierConfig:
    """Training configuration for the fault classifier."""

    window_size: int = 120
    step_size: int = 60
    test_size: float = 0.25
    random_state: int = 42
    n_estimators: int = 250
    max_depth: int | None = 18


@dataclass(frozen=True)
class FaultClassifierTrainingResult:
    """Result object returned after training."""

    model_path: str
    metrics_path: str
    report_path: str
    feature_count: int
    window_count: int
    class_count: int
    accuracy: float
    macro_f1: float
    weighted_f1: float
    classes: list[str]


def train_fault_classifier(
    *,
    input_csv_path: str | Path,
    model_path: str | Path,
    metrics_path: str | Path,
    report_path: str | Path,
    config: FaultClassifierConfig | None = None,
) -> FaultClassifierTrainingResult:
    """Train and save the ML fault classifier."""
    cfg = config or FaultClassifierConfig()
    input_path = Path(input_csv_path)
    data = pd.read_csv(input_path)

    features = build_window_features(
        data,
        window_size=cfg.window_size,
        step_size=cfg.step_size,
        include_labels=True,
    )
    if features.empty:
        raise ValueError("No feature windows were generated. Check input length and window size.")
    if "target_fault" not in features.columns:
        raise ValueError("Input data must contain fault_label to train the classifier.")

    feature_columns = _feature_columns(features)
    x_values = features[feature_columns]
    y_values = features["target_fault"].astype(str)

    if y_values.nunique() < 2:
        raise ValueError("At least two fault classes are required for classifier training.")

    stratify = y_values if y_values.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x_values,
        y_values,
        test_size=cfg.test_size,
        random_state=cfg.random_state,
        stratify=stratify,
    )

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=cfg.n_estimators,
                    max_depth=cfg.max_depth,
                    random_state=cfg.random_state,
                    class_weight="balanced_subsample",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    classes = sorted(y_values.unique().tolist())
    metrics = {
        "window_count": int(len(features)),
        "train_window_count": int(len(x_train)),
        "test_window_count": int(len(x_test)),
        "feature_count": int(len(feature_columns)),
        "class_count": int(len(classes)),
        "classes": classes,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 4),
        "classification_report": classification_report(y_test, predictions, zero_division=0, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=classes).tolist(),
        "feature_columns": feature_columns,
        "config": asdict(cfg),
    }

    artifact = {
        "model": model,
        "feature_columns": feature_columns,
        "config": asdict(cfg),
        "classes": classes,
    }

    model_output = Path(model_path)
    metrics_output = Path(metrics_path)
    report_output = Path(report_path)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(artifact, model_output)
    metrics_output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report_output.write_text(_metrics_to_markdown(metrics), encoding="utf-8")

    return FaultClassifierTrainingResult(
        model_path=str(model_output),
        metrics_path=str(metrics_output),
        report_path=str(report_output),
        feature_count=metrics["feature_count"],
        window_count=metrics["window_count"],
        class_count=metrics["class_count"],
        accuracy=metrics["accuracy"],
        macro_f1=metrics["macro_f1"],
        weighted_f1=metrics["weighted_f1"],
        classes=classes,
    )


def predict_fault_windows(
    *,
    input_csv_path: str | Path,
    model_path: str | Path,
    output_csv_path: str | Path,
) -> pd.DataFrame:
    """Run saved fault classifier and write window-level predictions."""
    artifact = joblib.load(Path(model_path))
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]
    config = artifact.get("config", {})

    data = pd.read_csv(input_csv_path)
    features = build_window_features(
        data,
        window_size=int(config.get("window_size", 120)),
        step_size=int(config.get("step_size", 60)),
        include_labels="fault_label" in data.columns,
    )
    if features.empty:
        raise ValueError("No feature windows were generated for prediction.")

    for column in feature_columns:
        if column not in features.columns:
            features[column] = 0.0

    x_values = features[feature_columns]
    predicted_faults = model.predict(x_values)

    output = features[["machine_id", "window_start_index", "window_start_time", "window_end_time"]].copy()
    if "target_fault" in features.columns:
        output["target_fault"] = features["target_fault"].astype(str)

    output["predicted_fault"] = predicted_faults.astype(str)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_values)
        classes = list(model.classes_)
        output["prediction_confidence"] = probabilities.max(axis=1).round(4)
        for class_index, class_name in enumerate(classes):
            output[f"prob_{class_name}"] = probabilities[:, class_index].round(4)
    else:
        output["prediction_confidence"] = 1.0

    output_path = Path(output_csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    return output


def _feature_columns(features: pd.DataFrame) -> list[str]:
    """Return ML feature columns."""
    columns = [column for column in features.columns if column not in NON_FEATURE_COLUMNS]
    if not columns:
        raise ValueError("No ML feature columns were produced.")
    return columns


def _metrics_to_markdown(metrics: dict[str, Any]) -> str:
    """Convert metrics dictionary to Markdown."""
    lines = [
        "# TwinAgent AI Fault Classifier Report",
        "",
        "## Summary",
        "",
        f"- Windows: {metrics['window_count']}",
        f"- Train windows: {metrics['train_window_count']}",
        f"- Test windows: {metrics['test_window_count']}",
        f"- Features: {metrics['feature_count']}",
        f"- Classes: {metrics['class_count']}",
        f"- Accuracy: {metrics['accuracy']}",
        f"- Macro F1: {metrics['macro_f1']}",
        f"- Weighted F1: {metrics['weighted_f1']}",
        "",
        "## Classes",
        "",
    ]

    for class_name in metrics["classes"]:
        lines.append(f"- `{class_name}`")

    lines.extend(["", "## Per-class scores", "", "| Class | Precision | Recall | F1 | Support |", "|---|---:|---:|---:|---:|"])
    report = metrics["classification_report"]
    for class_name in metrics["classes"]:
        if class_name not in report:
            continue
        values = report[class_name]
        lines.append(
            "| "
            f"{class_name} | "
            f"{round(values.get('precision', 0), 4)} | "
            f"{round(values.get('recall', 0), 4)} | "
            f"{round(values.get('f1-score', 0), 4)} | "
            f"{int(values.get('support', 0))} |"
        )

    lines.append("")
    return "\n".join(lines)
