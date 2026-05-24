r"""Reconcile rule and ML diagnoses into final incident diagnoses.

Run after ML incident enrichment:

    python scripts\reconcile_incident_diagnoses.py
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.ml import DiagnosisReconciliationConfig, export_reconciled_incident_diagnoses  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Reconcile TwinAgent rule and ML incident diagnoses.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents_with_ml.json",
        help="ML-enriched incidents JSON path.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents_reconciled.json",
        help="Output reconciled incidents JSON path.",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports" / "diagnosis_reconciliation_report.md",
        help="Output reconciliation Markdown report.",
    )
    parser.add_argument(
        "--high-confidence-threshold",
        type=float,
        default=0.85,
        help="ML confidence threshold for high-confidence diagnosis.",
    )
    parser.add_argument(
        "--medium-confidence-threshold",
        type=float,
        default=0.65,
        help="ML confidence threshold for medium-confidence diagnosis.",
    )
    return parser.parse_args()


def main() -> None:
    """Run reconciliation and print summary."""
    args = parse_args()
    config = DiagnosisReconciliationConfig(
        high_confidence_threshold=args.high_confidence_threshold,
        medium_confidence_threshold=args.medium_confidence_threshold,
    )

    reconciled = export_reconciled_incident_diagnoses(
        incidents_with_ml_path=args.input,
        output_json_path=args.output_json,
        output_markdown_path=args.output_markdown,
        config=config,
    )

    source_counts = Counter(str(incident.get("final_diagnosis_source", "unknown")) for incident in reconciled)
    final_counts = Counter(str(incident.get("final_diagnosis", "unknown")) for incident in reconciled)
    review_count = sum(1 for incident in reconciled if incident.get("requires_review") is True)

    print("TwinAgent AI diagnosis reconciliation complete.")
    print(f"Incidents reconciled: {len(reconciled)}")
    print(f"Incidents requiring review: {review_count}")
    print(f"Final diagnosis counts: {dict(final_counts)}")
    print(f"Decision source counts: {dict(source_counts)}")
    print(f"Reconciled incidents JSON: {args.output_json}")
    print(f"Reconciliation report Markdown: {args.output_markdown}")

    for incident in reconciled[:8]:
        print(
            "- "
            f"{incident['incident_id']} | rule={incident.get('suspected_fault')} | "
            f"ml={incident.get('ml_predicted_fault')} | "
            f"final={incident.get('final_diagnosis')} | "
            f"source={incident.get('final_diagnosis_source')} | "
            f"review={incident.get('requires_review')}"
        )


if __name__ == "__main__":
    main()
