r"""Run the TwinAgent AI ML fault classifier.

Run from the project root after training:

    python scripts\predict_faults.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.ml import predict_fault_windows  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Predict fault labels from processed sensor data.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Processed local sensor CSV.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=PROJECT_ROOT / "models" / "fault_classifier.joblib",
        help="Trained model artifact path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_fault_predictions.csv",
        help="Output prediction CSV path.",
    )
    return parser.parse_args()


def main() -> None:
    """Run saved classifier and export predictions."""
    args = parse_args()

    predictions = predict_fault_windows(
        input_csv_path=args.input,
        model_path=args.model,
        output_csv_path=args.output,
    )

    predicted_counts = predictions["predicted_fault"].value_counts().to_dict()

    print("TwinAgent AI fault prediction complete.")
    print(f"Prediction windows: {len(predictions)}")
    print(f"Predicted fault counts: {predicted_counts}")
    print(f"Prediction CSV saved: {args.output}")


if __name__ == "__main__":
    main()
