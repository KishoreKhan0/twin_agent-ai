r"""Enrich incident records with ML-assisted diagnosis.

Run after training and prediction:

    python scripts\enrich_incidents_with_ml.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.ml import export_ml_incident_diagnosis  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Add ML diagnosis fields to TwinAgent incidents.")
    parser.add_argument(
        "--incidents",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents.json",
        help="Input incidents JSON path.",
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_fault_predictions.csv",
        help="Fault prediction CSV path.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents_with_ml.json",
        help="Output enriched incidents JSON path.",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports" / "ml_incident_diagnosis_report.md",
        help="Output ML incident diagnosis Markdown report.",
    )
    parser.add_argument(
        "--low-confidence-threshold",
        type=float,
        default=0.6,
        help="Confidence threshold used for ML low-confidence incident flags.",
    )
    return parser.parse_args()


def main() -> None:
    """Enrich incidents and print compact summary."""
    args = parse_args()

    enriched = export_ml_incident_diagnosis(
        incidents_path=args.incidents,
        predictions_path=args.predictions,
        output_json_path=args.output_json,
        output_markdown_path=args.output_markdown,
        low_confidence_threshold=args.low_confidence_threshold,
    )

    with_ml = [incident for incident in enriched if incident.get("ml_predicted_fault")]
    disagreements = [incident for incident in with_ml if incident.get("diagnosis_agreement") is False]
    low_confidence = [incident for incident in with_ml if incident.get("ml_low_confidence") is True]

    print("TwinAgent AI ML incident diagnosis enrichment complete.")
    print(f"Incidents analyzed: {len(enriched)}")
    print(f"Incidents with ML windows: {len(with_ml)}")
    print(f"Rule/ML disagreements: {len(disagreements)}")
    print(f"Low-confidence ML incidents: {len(low_confidence)}")
    print(f"Enriched incidents JSON: {args.output_json}")
    print(f"Diagnosis report Markdown: {args.output_markdown}")

    for incident in enriched[:8]:
        print(
            "- "
            f"{incident['incident_id']} | rule={incident.get('suspected_fault')} | "
            f"ml={incident.get('ml_predicted_fault')} | "
            f"conf={incident.get('ml_confidence')} | "
            f"agree={incident.get('diagnosis_agreement')}"
        )


if __name__ == "__main__":
    main()
