"""Fleet dashboard helpers for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FleetDashboardPaths:
    """Path helper for optional fleet demo artifacts."""

    project_root: Path

    @property
    def fleet_root(self) -> Path:
        """Return fleet demo root directory."""
        return self.project_root / "data" / "fleet"

    @property
    def processed_data_path(self) -> Path:
        """Return processed fleet CSV path."""
        return self.fleet_root / "processed" / "fleet_sensor_data_with_anomalies.csv"

    @property
    def incidents_path(self) -> Path:
        """Return fleet incidents JSON path."""
        return self.fleet_root / "incidents" / "fleet_incidents.json"

    @property
    def summary_path(self) -> Path:
        """Return fleet summary JSON path."""
        return self.fleet_root / "reports" / "fleet_summary.json"


def fleet_artifacts_available(paths: FleetDashboardPaths) -> bool:
    """Return whether all required fleet dashboard artifacts exist."""
    return (
        paths.processed_data_path.exists()
        and paths.incidents_path.exists()
        and paths.summary_path.exists()
    )


def load_fleet_processed_data(path: str | Path) -> pd.DataFrame:
    """Load fleet processed sensor data."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Fleet processed data not found: {csv_path}")

    dataframe = pd.read_csv(csv_path)
    required_columns = {
        "timestamp",
        "machine_id",
        "temperature_c",
        "vibration_mm_s",
        "current_a",
        "health_score",
        "risk_level",
        "anomaly_score",
    }
    missing = required_columns.difference(dataframe.columns)
    if missing:
        raise ValueError(f"Fleet processed data is missing columns: {sorted(missing)}")

    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
    return dataframe


def load_fleet_incidents(path: str | Path) -> list[dict[str, Any]]:
    """Load fleet incidents JSON."""
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"Fleet incidents file not found: {json_path}")

    incidents = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(incidents, list):
        raise ValueError("Fleet incidents JSON must contain a list.")
    return incidents


def load_fleet_summary(path: str | Path) -> dict[str, Any]:
    """Load fleet summary JSON."""
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"Fleet summary file not found: {json_path}")

    summary = json.loads(json_path.read_text(encoding="utf-8"))
    if "fleet" not in summary or "machines" not in summary or "incidents" not in summary:
        raise ValueError("Fleet summary JSON must contain fleet, machines, and incidents.")
    return summary


def build_fleet_overview(summary: dict[str, Any]) -> dict[str, Any]:
    """Build top-level fleet overview metrics."""
    fleet = summary["fleet"]
    machines = summary["machines"]
    incidents = summary["incidents"]

    high_incidents = [incident for incident in incidents if incident.get("severity") == "high"]
    worst_machine = min(
        machines,
        key=lambda machine: machine.get("minimum_health_score", 100),
    )
    busiest_machine = max(
        machines,
        key=lambda machine: machine.get("incident_count", 0),
    )

    return {
        "machine_count": int(fleet["machine_count"]),
        "sensor_rows": int(fleet["sensor_rows"]),
        "incident_rows": int(fleet["incident_rows"]),
        "high_incidents": len(high_incidents),
        "time_start": fleet["time_start"],
        "time_end": fleet["time_end"],
        "worst_machine_id": worst_machine["machine_id"],
        "worst_machine_min_health": int(worst_machine["minimum_health_score"]),
        "busiest_machine_id": busiest_machine["machine_id"],
        "busiest_machine_incidents": int(busiest_machine["incident_count"]),
    }


def fleet_machine_table(summary: dict[str, Any]) -> pd.DataFrame:
    """Return machine-level fleet summary table."""
    rows = []
    for machine in summary["machines"]:
        rows.append(
            {
                "machine_id": machine["machine_id"],
                "line_id": machine["line_id"],
                "display_name": machine["display_name"],
                "rows": machine["rows"],
                "incidents": machine["incident_count"],
                "latest_health": machine["latest_health_score"],
                "min_health": machine["minimum_health_score"],
                "latest_risk": machine["latest_risk_level"],
                "anomaly_rows": machine["anomaly_rows"],
                "suspected_faults": ", ".join(machine.get("suspected_faults", [])) or "none",
            }
        )
    return pd.DataFrame(rows)


def fleet_incidents_table(incidents: list[dict[str, Any]]) -> pd.DataFrame:
    """Return fleet incidents as a dashboard-friendly table."""
    rows = []
    for incident in incidents:
        rows.append(
            {
                "incident_id": incident["incident_id"],
                "machine_id": incident["machine_id"],
                "line_id": incident.get("line_id", "unknown"),
                "severity": incident["severity"],
                "suspected_fault": incident["suspected_fault"],
                "start_time": incident["start_time"],
                "end_time": incident["end_time"],
                "duration_seconds": incident.get("duration_seconds"),
                "max_anomaly_score": incident.get("max_anomaly_score"),
                "contributing_sensors": ", ".join(incident.get("contributing_sensors", [])),
            }
        )
    return pd.DataFrame(rows)


def filter_fleet_machine(dataframe: pd.DataFrame, machine_id: str) -> pd.DataFrame:
    """Return processed sensor rows for one fleet machine."""
    return dataframe[dataframe["machine_id"] == machine_id].copy().sort_values("timestamp")


def incidents_for_machine(incidents: list[dict[str, Any]], machine_id: str) -> list[dict[str, Any]]:
    """Return fleet incidents for one machine."""
    return [incident for incident in incidents if incident.get("machine_id") == machine_id]
