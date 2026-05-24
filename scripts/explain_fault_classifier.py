r"""Export explainability artifacts for the TwinAgent AI fault classifier.

Run from the project root after training and prediction:

    python scripts\explain_fault_classifier.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.ml import ExplainabilityConfig, export_fault_classifier_explainability  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export ML explainability artifacts.")
    parser.add_argument(
        "--model",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier.joblib",
        help="Trained model artifact path.",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_metrics.json",
        help="Training metrics JSON path.",
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_fault_predictions.csv",
        help="Prediction CSV path.",
    )
    parser.add_argument(
        "--feature-importance-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_feature_importance.csv",
        help="Output feature importance CSV path.",
    )
    parser.add_argument(
        "--error-analysis-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_error_analysis.json",
        help="Output error-analysis JSON path.",
    )
    parser.add_argument(
        "--model-card-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_model_card.md",
        help="Output model card Markdown path.",
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "fault_prediction_audit.csv",
        help="Output prediction audit CSV path.",
    )
    parser.add_argument(
        "--low-confidence-threshold",
        type=float,
        default=0.6,
        help="Flag predictions below this confidence.",
    )
    return parser.parse_args()


def main() -> None:
    """Export explainability artifacts."""
    args = parse_args()

    result = export_fault_classifier_explainability(
        model_path=args.model,
        metrics_path=args.metrics,
        predictions_path=args.predictions,
        feature_importance_path=args.feature_importance_output,
        error_analysis_path=args.error_analysis_output,
        model_card_path=args.model_card_output,
        audit_csv_path=args.audit_output,
        config=ExplainabilityConfig(low_confidence_threshold=args.low_confidence_threshold),
    )

    print("TwinAgent AI fault classifier explainability export complete.")
    print(f"Top feature: {result.top_feature}")
    print(f"Low-confidence windows: {result.low_confidence_count}")
    if result.incorrect_count is not None:
        print(f"Incorrect windows: {result.incorrect_count}")
    print(f"Weak classes: {result.weak_classes}")
    print(f"Feature importance CSV: {result.feature_importance_path}")
    print(f"Error analysis JSON: {result.error_analysis_path}")
    print(f"Model card Markdown: {result.model_card_path}")
    print(f"Prediction audit CSV: {result.audit_csv_path}")


if __name__ == "__main__":
    main()
