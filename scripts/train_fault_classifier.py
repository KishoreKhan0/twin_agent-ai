r"""Train the TwinAgent AI ML fault classifier.

Run from the project root after generating local demo data:

    python scripts\train_fault_classifier.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.ml import FaultClassifierConfig, train_fault_classifier  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Train TwinAgent AI ML fault classifier.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Processed local sensor CSV with fault labels.",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier.joblib",
        help="Output model artifact path.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_metrics.json",
        help="Output metrics JSON path.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier_report.md",
        help="Output Markdown report path.",
    )
    parser.add_argument("--window-size", type=int, default=120, help="Rows per ML feature window.")
    parser.add_argument("--step-size", type=int, default=60, help="Rows between windows.")
    return parser.parse_args()


def main() -> None:
    """Train classifier and save model artifacts."""
    args = parse_args()

    config = FaultClassifierConfig(
        window_size=args.window_size,
        step_size=args.step_size,
    )

    result = train_fault_classifier(
        input_csv_path=args.input,
        model_path=args.model_output,
        metrics_path=args.metrics_output,
        report_path=args.report_output,
        config=config,
    )

    print("TwinAgent AI fault classifier training complete.")
    print(f"Training windows: {result.window_count}")
    print(f"Feature count: {result.feature_count}")
    print(f"Classes: {result.classes}")
    print(f"Accuracy: {result.accuracy}")
    print(f"Macro F1: {result.macro_f1}")
    print(f"Weighted F1: {result.weighted_f1}")
    print(f"Model saved: {result.model_path}")
    print(f"Metrics saved: {result.metrics_path}")
    print(f"Report saved: {result.report_path}")


if __name__ == "__main__":
    main()
