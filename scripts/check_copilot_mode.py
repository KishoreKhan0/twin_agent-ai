r"""Check that the TwinAgentCopilot supports selectable copilot modes.

Run from project root:

    python scripts\check_copilot_mode.py
"""

from __future__ import annotations

import inspect
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.agent import TwinAgentCopilot  # noqa: E402


def main() -> None:
    signature = inspect.signature(TwinAgentCopilot.answer_incident_question)
    print("TwinAgentCopilot.answer_incident_question signature:")
    print(signature)

    if "copilot_mode" in signature.parameters:
        print("OK: copilot_mode is supported.")
    else:
        print("ERROR: copilot_mode is NOT supported.")
        print(r"Replace src\twinagent\agent\agent_orchestrator.py and restart Streamlit.")


if __name__ == "__main__":
    main()
