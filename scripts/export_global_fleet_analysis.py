r"""Export global fleet incident analysis.

Run from the project root after generating fleet demo data:

    python scripts\export_global_fleet_analysis.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.fleet import answer_fleet_question, export_global_fleet_analysis, load_fleet_summary  # noqa: E402


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Export global TwinAgent AI fleet incident analysis.")
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "fleet_summary.json",
        help="Path to fleet_summary.json.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "global_fleet_analysis.json",
        help="Output global fleet analysis JSON path.",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "reports" / "global_fleet_analysis.md",
        help="Output global fleet analysis Markdown path.",
    )
    args = parser.parse_args()

    payload = export_global_fleet_analysis(
        summary_path=args.summary_path,
        output_json_path=args.output_json,
        output_markdown_path=args.output_markdown,
    )

    summary = load_fleet_summary(args.summary_path)
    sample_answer = answer_fleet_question(summary, "Compare bearing wear incidents.")

    print("TwinAgent AI global fleet analysis export complete.")
    print(f"Fault patterns analyzed: {len(payload['fault_patterns'])}")
    print(f"JSON report: {args.output_json}")
    print(f"Markdown report: {args.output_markdown}")
    print("Sample global fleet copilot answer:")
    print(sample_answer.answer)


if __name__ == "__main__":
    main()
