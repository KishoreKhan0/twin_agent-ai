r"""Export TwinAgent AI fleet triage reports.

Run from the project root after generating fleet demo data:

    python scripts\export_fleet_triage.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.fleet import export_fleet_triage_report  # noqa: E402


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Export TwinAgent AI fleet triage report.")
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "fleet_summary.json",
        help="Path to fleet_summary.json.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "fleet_triage.json",
        help="Output fleet triage JSON path.",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "fleet_triage.md",
        help="Output fleet triage Markdown path.",
    )
    args = parser.parse_args()

    triage = export_fleet_triage_report(
        summary_path=args.summary_path,
        output_json_path=args.output_json,
        output_markdown_path=args.output_markdown,
    )

    print("TwinAgent AI fleet triage export complete.")
    print(f"Machines triaged: {len(triage.machine_triage)}")
    print(f"Incidents triaged: {len(triage.incident_triage)}")
    if triage.top_machine:
        print(
            "Top machine priority: "
            f"{triage.top_machine.machine_id} | "
            f"{triage.top_machine.priority_level} | "
            f"score={triage.top_machine.priority_score}"
        )
    if triage.top_incident:
        print(
            "Top incident priority: "
            f"{triage.top_incident.incident_id} | "
            f"{triage.top_incident.priority_level} | "
            f"score={triage.top_incident.priority_score}"
        )
    print(f"JSON report: {args.output_json}")
    print(f"Markdown report: {args.output_markdown}")


if __name__ == "__main__":
    main()
