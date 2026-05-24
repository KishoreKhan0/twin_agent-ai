"""Model artifact helpers for TwinAgent AI ML components."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


def load_model_artifact(model_path: str | Path) -> dict[str, Any]:
    """Load a saved joblib model artifact."""
    return joblib.load(Path(model_path))


def save_model_artifact(artifact: dict[str, Any], model_path: str | Path) -> None:
    """Save a joblib model artifact."""
    output_path = Path(model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)
