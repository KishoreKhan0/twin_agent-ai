r"""Bootstrap TwinAgent AI demo data.

This script generates the full local demo artifact set used by the API,
dashboard, evaluation module, and report exporter.

Run from the project root:

    python scripts\bootstrap_demo_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.agent import IncidentReportWriter  # noqa: E402
from twinagent.analytics import (  # noqa: E402
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.analytics.incident_segments import expand_incident_episodes  # noqa: E402
from twinagent.evaluation import EvaluationBenchmark  # noqa: E402
from twinagent.simulation import MachineSimulator  # noqa: E402
from twinagent.storage import SQLiteRepository  # noqa: E402


def default_local_config_path() -> Path:
    """Return rich local demo config path, falling back to compact config."""
    rich_config = PROJECT_ROOT / "configs" / "local_demo_config.yaml"
    if rich_config.exists():
        return rich_config
    return PROJECT_ROOT / "configs" / "machine_config.yaml"


def main() -> None:
    """Generate all demo artifacts for local or Docker execution."""
    data_generated = PROJECT_ROOT / "data" / "generated"
    data_processed = PROJECT_ROOT / "data" / "processed"
    data_incidents = PROJECT_ROOT / "data" / "incidents"
    data_reports = PROJECT_ROOT / "data" / "reports"

    for directory in [data_generated, data_processed, data_incidents, data_reports]:
        directory.mkdir(parents=True, exist_ok=True)

    sensor_data_path = data_generated / "sensor_data.csv"
    processed_path = data_processed / "sensor_data_with_anomalies.csv"
    incidents_path = data_incidents / "incidents.json"
    database_path = data_processed / "twinagent.db"

    local_config_path = default_local_config_path()
    simulator = MachineSimulator.from_config_file(local_config_path)
    raw_data = simulator.simulate()
    raw_data.to_csv(sensor_data_path, index=False)

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(raw_data)

    health = HealthScoreCalculator()
    processed = health.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    processed = advisor.add_maintenance_columns(processed)

    with (PROJECT_ROOT / "configs" / "anomaly_config.yaml").open("r", encoding="utf-8") as file:
        anomaly_config = yaml.safe_load(file)

    raw_incidents = IncidentDetector.from_config(anomaly_config).detect_incidents(processed)
    incidents = expand_incident_episodes(raw_incidents)

    processed.to_csv(processed_path, index=False)
    incidents_path.write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    repository = SQLiteRepository(database_path=database_path)
    repository.initialize()
    sensor_rows = repository.write_sensor_readings(processed, replace=True)
    incident_rows = repository.write_incidents(incidents, replace=True)

    benchmark = EvaluationBenchmark(
        processed_data_path=processed_path,
        incidents_path=incidents_path,
    )
    benchmark.save_json(data_reports / "evaluation_metrics.json")
    benchmark.save_markdown(data_reports / "evaluation_report.md")

    if incidents:
        writer = IncidentReportWriter.from_project_root(PROJECT_ROOT)
        writer.write_report(incident_id=incidents[0]["incident_id"], output_dir=data_reports)

    print("TwinAgent AI demo data bootstrap complete.")
    print(f"Local config used: {local_config_path}")
    print(f"Raw sensor CSV: {sensor_data_path}")
    print(f"Processed CSV: {processed_path}")
    print(f"Incidents JSON: {incidents_path}")
    print(f"SQLite database: {database_path}")
    print(f"Sensor rows written: {sensor_rows}")
    print(f"Raw detector incidents: {len(raw_incidents)}")
    print(f"Operational incidents written: {incident_rows}")
    print(f"Reports directory: {data_reports}")


if __name__ == "__main__":
    main()
