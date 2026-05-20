"""Run the TwinAgent AI copilot on an incident question.

Run from the project root after generating data and incidents:

    python scripts\run_agent.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.agent import TwinAgentCopilot  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the TwinAgent AI copilot.")
    parser.add_argument(
        "--incident-id",
        default="INC-0001",
        help="Incident ID to explain.",
    )
    parser.add_argument(
        "--question",
        default="Why did this incident trigger and what should the technician inspect first?",
        help="Question for the copilot.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the deterministic copilot and print the answer."""
    args = parse_args()

    copilot = TwinAgentCopilot.from_project_root(PROJECT_ROOT)
    answer = copilot.answer_incident_question(
        incident_id=args.incident_id,
        question=args.question,
    )

    print(answer)


if __name__ == "__main__":
    main()
