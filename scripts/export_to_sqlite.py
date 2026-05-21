r"""Export TwinAgent AI processed outputs to SQLite.

Run from the project root after generating data and incidents:

    python scripts\export_to_sqlite.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.storage import SQLiteRepository  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export TwinAgent AI outputs to SQLite.")
    parser.add_argument(
        "--processed-data",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Processed CSV with anomaly, health, and maintenance columns.",
    )
    parser.add_argument(
        "--incidents",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents.json",
        help="Generated incidents JSON.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "twinagent.db",
        help="SQLite database output path.",
    )
    return parser.parse_args()


def main() -> None:
    """Export processed data and incidents to SQLite."""
    args = parse_args()

    if not args.processed_data.exists():
        raise FileNotFoundError(
            f"Processed data not found: {args.processed_data}. "
            r"Run python scripts\run_anomaly_detection.py first."
        )
    if not args.incidents.exists():
        raise FileNotFoundError(
            f"Incidents file not found: {args.incidents}. "
            r"Run python scripts\run_anomaly_detection.py first."
        )

    dataframe = pd.read_csv(args.processed_data)
    incidents = json.loads(args.incidents.read_text(encoding="utf-8"))

    repository = SQLiteRepository(database_path=args.database)
    repository.initialize()
    sensor_count = repository.write_sensor_readings(dataframe, replace=True)
    incident_count = repository.write_incidents(incidents, replace=True)

    latest = repository.get_latest_machine_state(machine_id="line1_motor1")

    print("TwinAgent AI SQLite export complete.")
    print(f"Database: {args.database}")
    print(f"Sensor rows written: {sensor_count}")
    print(f"Incidents written: {incident_count}")
    print(f"Latest machine state: {latest['machine_state']}")
    print(f"Latest health score: {latest['health_score']}")
    print(f"Latest risk level: {latest['risk_level']}")


if __name__ == "__main__":
    main()
