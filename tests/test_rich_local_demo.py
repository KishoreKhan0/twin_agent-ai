"""Tests for rich local demo generation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_rich_local_bootstrap_generates_more_data_and_incidents() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/bootstrap_demo_data.py"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "TwinAgent AI demo data bootstrap complete." in result.stdout
    assert "Operational incidents written:" in result.stdout

    sensor_path = PROJECT_ROOT / "data" / "generated" / "sensor_data.csv"
    incidents_path = PROJECT_ROOT / "data" / "incidents" / "incidents.json"

    dataframe = pd.read_csv(sensor_path)
    incidents = json.loads(incidents_path.read_text(encoding="utf-8"))

    assert len(dataframe) >= 21600
    assert len(incidents) >= 10
    assert incidents[0]["incident_id"] == "INC-0001"
