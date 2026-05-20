"""Run anomaly detection and incident generation for TwinAgent AI.

Run from the project root:

    python scripts\run_anomaly_detection.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.analytics import AnomalyDetector, IncidentDetector  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run TwinAgent AI anomaly detection.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "generated" / "sensor_data.csv",
        help="Input synthetic sensor CSV.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "anomaly_config.yaml",
        help="Path to anomaly detection config.",
    )
    parser.add_argument(
        "--processed-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Output CSV with anomaly columns.",
    )
    parser.add_argument(
        "--incidents-output",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents.json",
        help="Output incident JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    """Run anomaly detection and save the processed outputs."""
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input data not found: {args.input}. "
            "Run python scripts\generate_synthetic_data.py first."
        )

    dataframe = pd.read_csv(args.input)

    detector = AnomalyDetector.from_config_file(args.config)
    processed = detector.detect(dataframe)

    with args.config.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    incident_detector = IncidentDetector.from_config(config)
    incidents = incident_detector.detect_incidents(processed)

    args.processed_output.parent.mkdir(parents=True, exist_ok=True)
    args.incidents_output.parent.mkdir(parents=True, exist_ok=True)

    processed.to_csv(args.processed_output, index=False)

    with args.incidents_output.open("w", encoding="utf-8") as file:
        json.dump(incidents, file, indent=2)

    anomaly_count = int(processed["is_anomaly"].sum())
    severity_counts = processed["anomaly_severity"].value_counts().to_dict()

    print("TwinAgent AI anomaly detection complete.")
    print(f"Input rows: {len(processed)}")
    print(f"Anomaly rows: {anomaly_count}")
    print(f"Anomaly severity counts: {severity_counts}")
    print(f"Incidents created: {len(incidents)}")

    for incident in incidents:
        print(
            f"- {incident['incident_id']} | {incident['severity']} | "
            f"{incident['suspected_fault']} | "
            f"{incident['start_time']} -> {incident['end_time']}"
        )

    print(f"Processed CSV: {args.processed_output}")
    print(f"Incidents JSON: {args.incidents_output}")


if __name__ == "__main__":
    main()
