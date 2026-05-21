r"""Launch the TwinAgent AI FastAPI backend.

Run from the project root after exporting SQLite data:

    python scripts\launch_api.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Launch the FastAPI backend using uvicorn."""
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "twinagent.api.main:app",
        "--app-dir",
        str(PROJECT_ROOT / "src"),
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    main()
