r"""Launch the TwinAgent AI FastAPI app.

Run from the project root:

    python scripts\launch_api.py

Swagger UI:

    http://localhost:8000/docs
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    """Launch the API server."""
    host = os.getenv("TWINAGENT_API_HOST", "0.0.0.0")
    port = int(os.getenv("TWINAGENT_API_PORT", "8000"))
    reload = os.getenv("TWINAGENT_API_RELOAD", "0") == "1"

    uvicorn.run(
        "twinagent.api.app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
