"""Reusable dashboard data-loading and summary components for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DashboardPaths:
    """Default file paths used by the Streamlit dashboard."""

    project_root: Path

    @property
    def processed_data_path(self) -> Path:
        """Path to processed sensor data with anomaly and health columns."""
        return self.project_root / "data" / "processed" / "sensor_data_with_anomalies.csv"

    @property
    def incidents_path(self) -> Path:
        """Path to generated incident records."""
        return self.project_root / "data" / "incidents" / "incidents.json"


def load_processed_data(path: str | Path) -> pd.DataFrame:
    """Load processed sensor data for dashboard display."""
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(
            f"Processed data not found: {data_path}. "
            "Run python scripts\\generate_synthetic_data.py and "
            "python scripts\\run_anomaly_detection.py first."
        )

    dataframe = pd.read_csv(data_path)
    if dataframe.empty:
        raise ValueError(f"Processed data file is empty: {data_path}")

    required_columns = {
        "timestamp",
        "machine_id",
        "temperature_c",
        "vibration_mm_s",
        "rpm",
        "current_a",
        "anomaly_score",
        "anomaly_severity",
        "health_score",
        "risk_level",
        "maintenance_urgency",
        "maintenance_recommendation",
    }
    missing = required_columns - set(dataframe.columns)
    if missing:
        raise ValueError(
            "Processed data is missing required dashboard columns: "
            + ", ".join(sorted(missing))
        )

    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
    return dataframe


def load_incidents(path: str | Path) -> list[dict[str, Any]]:
    """Load incident JSON records for dashboard display."""
    incidents_path = Path(path)
    if not incidents_path.exists():
        raise FileNotFoundError(
            f"Incidents file not found: {incidents_path}. "
            "Run python scripts\\run_anomaly_detection.py first."
        )

    with incidents_path.open("r", encoding="utf-8") as file:
        incidents = json.load(file)

    if not isinstance(incidents, list):
        raise ValueError("Incidents JSON must contain a list.")

    return incidents


def build_machine_overview(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Build high-level overview metrics for the current machine state."""
    if dataframe.empty:
        raise ValueError("Cannot build dashboard overview from empty data.")

    latest = dataframe.sort_values("timestamp").iloc[-1]
    anomaly_rows = int(dataframe["is_anomaly"].sum()) if "is_anomaly" in dataframe else 0

    return {
        "machine_id": str(latest["machine_id"]),
        "latest_timestamp": latest["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(latest["timestamp"], "strftime")
        else str(latest["timestamp"]),
        "machine_state": str(latest.get("machine_state", "unknown")),
        "health_score": int(latest["health_score"]),
        "risk_level": str(latest["risk_level"]),
        "latest_anomaly_score": round(float(latest["anomaly_score"]), 4),
        "latest_maintenance_urgency": str(latest["maintenance_urgency"]),
        "anomaly_rows": anomaly_rows,
        "total_rows": int(len(dataframe)),
        "min_health_score": int(dataframe["health_score"].min()),
        "max_anomaly_score": round(float(dataframe["anomaly_score"].max()), 4),
    }


def build_incident_summary(incident: dict[str, Any]) -> dict[str, Any]:
    """Return a dashboard-friendly incident summary."""
    required_keys = {
        "incident_id",
        "machine_id",
        "start_time",
        "end_time",
        "severity",
        "suspected_fault",
        "max_anomaly_score",
        "contributing_sensors",
        "evidence",
    }
    missing = required_keys - set(incident)
    if missing:
        raise ValueError("Incident is missing required keys: " + ", ".join(sorted(missing)))

    return {
        "incident_id": incident["incident_id"],
        "machine_id": incident["machine_id"],
        "time_window": f"{incident['start_time']} → {incident['end_time']}",
        "severity": incident["severity"],
        "suspected_fault": incident["suspected_fault"],
        "max_anomaly_score": incident["max_anomaly_score"],
        "contributing_sensors": ", ".join(incident.get("contributing_sensors", [])),
        "evidence": incident.get("evidence", {}),
    }


def incidents_to_dataframe(incidents: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert incident records to a compact dashboard dataframe."""
    if not incidents:
        return pd.DataFrame(
            columns=[
                "incident_id",
                "machine_id",
                "start_time",
                "end_time",
                "severity",
                "suspected_fault",
                "max_anomaly_score",
                "duration_seconds",
            ]
        )

    columns = [
        "incident_id",
        "machine_id",
        "start_time",
        "end_time",
        "severity",
        "suspected_fault",
        "max_anomaly_score",
        "duration_seconds",
    ]
    return pd.DataFrame([{column: incident.get(column) for column in columns} for incident in incidents])
