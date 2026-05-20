r"""Export a TwinAgent AI incident report as Markdown.

Run from the project root after generating data and incidents:

    python scripts\export_incident_report.py --incident-id INC-0001
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.agent import IncidentReportWriter  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export a TwinAgent AI incident report.")
    parser.add_argument(
        "--incident-id",
        default="INC-0001",
        help="Incident ID to export.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports",
        help="Directory where the Markdown report should be saved.",
    )
    parser.add_argument(
        "--question",
        default="Why did this incident trigger and what should the technician inspect first?",
        help="Question used to retrieve relevant engineering references.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate and write the incident report."""
    args = parse_args()

    writer = IncidentReportWriter.from_project_root(PROJECT_ROOT)
    report_path = writer.write_report(
        incident_id=args.incident_id,
        output_dir=args.output_dir,
        question=args.question,
    )

    print("TwinAgent AI incident report export complete.")
    print(f"Incident ID: {args.incident_id}")
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()
