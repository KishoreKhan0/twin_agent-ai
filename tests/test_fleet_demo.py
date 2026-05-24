"""Tests for the TwinAgent AI fleet demo generator."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generate_fleet_demo_data_script_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_fleet_demo_data.py"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "TwinAgent AI fleet demo generation complete." in result.stdout
    assert "Machines generated: 12" in result.stdout

    processed_path = PROJECT_ROOT / "data" / "fleet" / "processed" / "fleet_sensor_data_with_anomalies.csv"
    incidents_path = PROJECT_ROOT / "data" / "fleet" / "incidents" / "fleet_incidents.json"
    database_path = PROJECT_ROOT / "data" / "fleet" / "processed" / "twinagent_fleet.db"
    summary_path = PROJECT_ROOT / "data" / "fleet" / "reports" / "fleet_summary.json"

    assert processed_path.exists()
    assert incidents_path.exists()
    assert database_path.exists()
    assert summary_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["fleet"]["machine_count"] == 12
    assert summary["fleet"]["sensor_rows"] == 43200
    assert len(summary["machines"]) == 12
    assert summary["fleet"]["incident_rows"] >= 20
    assert summary["fleet"]["incident_segmentation"]["enabled"] is True
