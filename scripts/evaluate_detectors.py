r"""Evaluate TwinAgent AI anomaly detection outputs.

Run from the project root after data generation and anomaly detection:

    python scripts\evaluate_detectors.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.evaluation import EvaluationBenchmark  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate TwinAgent AI detector outputs.")
    parser.add_argument(
        "--processed-data",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Processed CSV with anomaly and health columns.",
    )
    parser.add_argument(
        "--incidents",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents.json",
        help="Generated incidents JSON.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports" / "evaluation_metrics.json",
        help="Output path for JSON metrics.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports" / "evaluation_report.md",
        help="Output path for Markdown report.",
    )
    return parser.parse_args()


def main() -> None:
    """Run evaluation and write benchmark artifacts."""
    args = parse_args()

    benchmark = EvaluationBenchmark(
        processed_data_path=args.processed_data,
        incidents_path=args.incidents,
    )

    report = benchmark.run()
    benchmark.save_json(args.json_output)
    benchmark.save_markdown(args.markdown_output)

    binary = report["binary_detection"]
    delay = report["detection_delay"]
    overlap = report["incident_overlap"]
    row_classification = report["row_fault_classification"]
    incident_diagnosis = report["incident_diagnosis"]

    print("TwinAgent AI evaluation complete.")
    print(f"Rows evaluated: {report['summary']['rows']}")
    print(f"Precision: {binary['precision']}")
    print(f"Recall: {binary['recall']}")
    print(f"F1 score: {binary['f1_score']}")
    print(f"False positive rate: {binary['false_positive_rate']}")
    print(f"Mean detection delay seconds: {delay['mean_detection_delay_seconds']}")
    print(f"Incident overlap score: {overlap['incident_overlap_score']}")
    print(f"Incident diagnosis accuracy: {incident_diagnosis['incident_diagnosis_accuracy']}")
    print(f"Row-level fault alignment accuracy: {row_classification['row_alignment_accuracy']}")
    print(f"JSON metrics: {args.json_output}")
    print(f"Markdown report: {args.markdown_output}")

    # Keep a compact machine-readable line useful for logs.
    print("Compact metrics:")
    print(
        json.dumps(
            {
                "precision": binary["precision"],
                "recall": binary["recall"],
                "f1_score": binary["f1_score"],
                "false_positive_rate": binary["false_positive_rate"],
                "incident_overlap_score": overlap["incident_overlap_score"],
                "incident_diagnosis_accuracy": incident_diagnosis["incident_diagnosis_accuracy"],
                "row_fault_alignment_accuracy": row_classification["row_alignment_accuracy"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
