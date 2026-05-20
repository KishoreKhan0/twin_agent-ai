r"""Launch the TwinAgent AI Streamlit dashboard.

Run from the project root:

    python scripts\launch_dashboard.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_APP = PROJECT_ROOT / "src" / "twinagent" / "dashboard" / "streamlit_app.py"


def main() -> None:
    """Launch the Streamlit dashboard."""
    if not DASHBOARD_APP.exists():
        raise FileNotFoundError(f"Dashboard app not found: {DASHBOARD_APP}")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(DASHBOARD_APP),
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    main()
