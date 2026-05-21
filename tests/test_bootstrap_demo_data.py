"""Tests for the TwinAgent AI demo-data bootstrap script."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_demo_data_script_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/bootstrap_demo_data.py"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "TwinAgent AI demo data bootstrap complete." in result.stdout
    assert (PROJECT_ROOT / "data" / "generated" / "sensor_data.csv").exists()
    assert (PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv").exists()
    assert (PROJECT_ROOT / "data" / "processed" / "twinagent.db").exists()
    assert (PROJECT_ROOT / "data" / "incidents" / "incidents.json").exists()
    assert (PROJECT_ROOT / "data" / "reports" / "evaluation_report.md").exists()
    assert (PROJECT_ROOT / "data" / "reports" / "INC-0001_report.md").exists()
