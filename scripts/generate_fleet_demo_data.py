r"""Generate a multi-machine TwinAgent AI fleet demo dataset.

This script keeps the original single-machine pipeline untouched and creates an
additional fleet-level demo dataset for realistic fleet operations.

Run from the project root:

    python scripts\generate_fleet_demo_data.py

The generator intentionally creates a larger fleet and segments long anomaly
windows into operational incident episodes. That gives the dashboard enough
incident volume for global comparison questions.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.analytics import (  # noqa: E402
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation import MachineSimulator  # noqa: E402
from twinagent.storage import SQLiteRepository  # noqa: E402


ANOMALY_CONFIG_PATH = PROJECT_ROOT / "configs" / "anomaly_config.yaml"
SEGMENT_LONG_INCIDENTS_AFTER_SECONDS = 420
TARGET_SEGMENT_SECONDS = 300
MAX_SEGMENTS_PER_INCIDENT = 6


FLEET_MACHINES = [
    {"machine_id": "line1_motor1", "line_id": "line1", "display_name": "Line 1 Conveyor Motor 1", "time_offset_minutes": 0, "temperature_offset": 0.0, "vibration_multiplier": 1.00, "current_multiplier": 1.00, "load_offset": 0.0},
    {"machine_id": "line1_motor2", "line_id": "line1", "display_name": "Line 1 Conveyor Motor 2", "time_offset_minutes": 70, "temperature_offset": 4.5, "vibration_multiplier": 1.25, "current_multiplier": 1.08, "load_offset": 3.0},
    {"machine_id": "line2_motor1", "line_id": "line2", "display_name": "Line 2 Conveyor Motor 1", "time_offset_minutes": 140, "temperature_offset": -2.0, "vibration_multiplier": 0.88, "current_multiplier": 0.96, "load_offset": -2.0},
    {"machine_id": "line2_motor2", "line_id": "line2", "display_name": "Line 2 Conveyor Motor 2", "time_offset_minutes": 210, "temperature_offset": 6.0, "vibration_multiplier": 1.35, "current_multiplier": 1.12, "load_offset": 5.0},
    {"machine_id": "line3_motor1", "line_id": "line3", "display_name": "Line 3 Conveyor Motor 1", "time_offset_minutes": 280, "temperature_offset": 2.5, "vibration_multiplier": 1.08, "current_multiplier": 1.04, "load_offset": 1.5},
    {"machine_id": "line3_motor2", "line_id": "line3", "display_name": "Line 3 Conveyor Motor 2", "time_offset_minutes": 350, "temperature_offset": 7.5, "vibration_multiplier": 1.45, "current_multiplier": 1.16, "load_offset": 6.0},
    {"machine_id": "line4_motor1", "line_id": "line4", "display_name": "Line 4 Conveyor Motor 1", "time_offset_minutes": 420, "temperature_offset": 3.5, "vibration_multiplier": 1.18, "current_multiplier": 1.06, "load_offset": 2.0},
    {"machine_id": "line4_motor2", "line_id": "line4", "display_name": "Line 4 Conveyor Motor 2", "time_offset_minutes": 490, "temperature_offset": 9.0, "vibration_multiplier": 1.55, "current_multiplier": 1.20, "load_offset": 8.0},
    {"machine_id": "line5_motor1", "line_id": "line5", "display_name": "Line 5 Conveyor Motor 1", "time_offset_minutes": 560, "temperature_offset": 1.5, "vibration_multiplier": 1.12, "current_multiplier": 1.02, "load_offset": 1.0},
    {"machine_id": "line5_motor2", "line_id": "line5", "display_name": "Line 5 Conveyor Motor 2", "time_offset_minutes": 630, "temperature_offset": 10.5, "vibration_multiplier": 1.70, "current_multiplier": 1.25, "load_offset": 10.0},
    {"machine_id": "line6_motor1", "line_id": "line6", "display_name": "Line 6 Conveyor Motor 1", "time_offset_minutes": 700, "temperature_offset": 5.0, "vibration_multiplier": 1.28, "current_multiplier": 1.10, "load_offset": 4.0},
    {"machine_id": "line6_motor2", "line_id": "line6", "display_name": "Line 6 Conveyor Motor 2", "time_offset_minutes": 770, "temperature_offset": 12.0, "vibration_multiplier": 1.85, "current_multiplier": 1.30, "load_offset": 12.0},
]


def main() -> None:
    """Generate fleet-level processed data, incidents, SQLite DB, and summary reports."""
    output_dir = PROJECT_ROOT / "data" / "fleet"
    generated_dir = output_dir / "generated"
    processed_dir = output_dir / "processed"
    incidents_dir = output_dir / "incidents"
    reports_dir = output_dir / "reports"

    for directory in [generated_dir, processed_dir, incidents_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    raw_frames: list[pd.DataFrame] = []
    processed_frames: list[pd.DataFrame] = []
    all_incidents: list[dict[str, Any]] = []

    anomaly_config = _load_anomaly_config()

    for machine_number, machine in enumerate(FLEET_MACHINES, start=1):
        raw = _generate_machine_data(machine=machine)
        processed = _run_machine_analytics(raw=raw)
        incidents = _detect_machine_incidents(
            processed=processed,
            anomaly_config=anomaly_config,
            machine_number=machine_number,
        )

        raw_frames.append(raw)
        processed_frames.append(processed)
        all_incidents.extend(incidents)

    fleet_raw = pd.concat(raw_frames, ignore_index=True).sort_values(["machine_id", "timestamp"])
    fleet_processed = pd.concat(processed_frames, ignore_index=True).sort_values(["machine_id", "timestamp"])
    all_incidents = sorted(all_incidents, key=lambda incident: (incident["start_time"], incident["incident_id"]))

    raw_path = generated_dir / "fleet_sensor_data.csv"
    processed_path = processed_dir / "fleet_sensor_data_with_anomalies.csv"
    incidents_path = incidents_dir / "fleet_incidents.json"
    database_path = processed_dir / "twinagent_fleet.db"

    fleet_raw.to_csv(raw_path, index=False)
    fleet_processed.to_csv(processed_path, index=False)
    incidents_path.write_text(json.dumps(all_incidents, indent=2), encoding="utf-8")

    repository = SQLiteRepository(database_path=database_path)
    repository.initialize()
    sensor_rows = repository.write_sensor_readings(fleet_processed, replace=True)
    incident_rows = repository.write_incidents(all_incidents, replace=True)

    summary = _build_fleet_summary(
        processed=fleet_processed,
        incidents=all_incidents,
        sensor_rows=sensor_rows,
        incident_rows=incident_rows,
    )
    summary_path = reports_dir / "fleet_summary.json"
    summary_md_path = reports_dir / "fleet_summary.md"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary_md_path.write_text(_summary_to_markdown(summary), encoding="utf-8")

    print("TwinAgent AI fleet demo generation complete.")
    print(f"Machines generated: {len(FLEET_MACHINES)}")
    print(f"Sensor rows written: {sensor_rows}")
    print(f"Incidents written: {incident_rows}")
    print(f"Fleet raw CSV: {raw_path}")
    print(f"Fleet processed CSV: {processed_path}")
    print(f"Fleet incidents JSON: {incidents_path}")
    print(f"Fleet SQLite database: {database_path}")
    print(f"Fleet summary JSON: {summary_path}")
    print(f"Fleet summary Markdown: {summary_md_path}")

    print("\nMachine summary:")
    for machine_summary in summary["machines"]:
        print(
            "- "
            f"{machine_summary['machine_id']} | rows={machine_summary['rows']} | "
            f"incidents={machine_summary['incident_count']} | "
            f"latest_health={machine_summary['latest_health_score']} | "
            f"latest_risk={machine_summary['latest_risk_level']}"
        )


def _load_anomaly_config() -> dict[str, Any]:
    """Load anomaly detector configuration."""
    with ANOMALY_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _generate_machine_data(machine: dict[str, Any]) -> pd.DataFrame:
    """Generate one machine's synthetic sensor dataframe."""
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate().copy()

    dataframe["machine_id"] = machine["machine_id"]
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"]) + pd.Timedelta(
        minutes=machine["time_offset_minutes"]
    )
    dataframe["timestamp"] = dataframe["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    dataframe["temperature_c"] = dataframe["temperature_c"] + machine["temperature_offset"]
    dataframe["vibration_mm_s"] = dataframe["vibration_mm_s"] * machine["vibration_multiplier"]
    dataframe["current_a"] = dataframe["current_a"] * machine["current_multiplier"]

    if "load_pct" in dataframe.columns:
        dataframe["load_pct"] = (dataframe["load_pct"] + machine["load_offset"]).clip(lower=0, upper=100)

    return dataframe


def _run_machine_analytics(raw: pd.DataFrame) -> pd.DataFrame:
    """Run anomaly detection, health scoring, and maintenance advisory."""
    detector = AnomalyDetector.from_config_file(ANOMALY_CONFIG_PATH)
    processed = detector.detect(raw)

    health = HealthScoreCalculator()
    processed = health.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    processed = advisor.add_maintenance_columns(processed)

    return processed


def _detect_machine_incidents(
    processed: pd.DataFrame,
    anomaly_config: dict[str, Any],
    machine_number: int,
) -> list[dict[str, Any]]:
    """Detect incidents, remap IDs, and split long incidents into episodes."""
    if hasattr(IncidentDetector, "from_config"):
        detector = IncidentDetector.from_config(anomaly_config)
    else:
        detector = IncidentDetector.from_config_file(ANOMALY_CONFIG_PATH)

    detected_incidents = detector.detect_incidents(processed)

    remapped: list[dict[str, Any]] = []
    for incident_index, incident in enumerate(detected_incidents, start=1):
        base_incident = dict(incident)
        base_incident["line_id"] = _line_id_for_machine(str(base_incident["machine_id"]))
        base_incident["display_name"] = _display_name_for_machine(str(base_incident["machine_id"]))
        base_incident["parent_incident_id"] = f"FLEET-M{machine_number:02d}-{incident_index:04d}"

        segmented = _segment_incident(
            incident=base_incident,
            machine_number=machine_number,
            incident_index=incident_index,
        )
        remapped.extend(segmented)

    return remapped


def _segment_incident(
    incident: dict[str, Any],
    machine_number: int,
    incident_index: int,
) -> list[dict[str, Any]]:
    """Split long operational incidents into smaller fleet episodes."""
    duration = int(incident.get("duration_seconds", 0))
    severity = str(incident.get("severity", "none")).lower()

    if severity == "low" or duration <= SEGMENT_LONG_INCIDENTS_AFTER_SECONDS:
        updated = dict(incident)
        updated["incident_id"] = f"FLEET-M{machine_number:02d}-{incident_index:04d}"
        updated["episode_index"] = 1
        updated["episode_count"] = 1
        return [updated]

    segment_count = min(
        MAX_SEGMENTS_PER_INCIDENT,
        max(2, math.ceil(duration / TARGET_SEGMENT_SECONDS)),
    )

    start_time = pd.Timestamp(incident["start_time"])
    end_time = pd.Timestamp(incident["end_time"])
    total_seconds = max(1, int((end_time - start_time).total_seconds()))

    segments: list[dict[str, Any]] = []
    for segment_index in range(segment_count):
        segment_start_seconds = round((segment_index / segment_count) * total_seconds)
        segment_end_seconds = round(((segment_index + 1) / segment_count) * total_seconds)

        segment_start = start_time + pd.Timedelta(seconds=segment_start_seconds)
        segment_end = start_time + pd.Timedelta(seconds=segment_end_seconds)

        if segment_index == segment_count - 1:
            segment_end = end_time

        updated = dict(incident)
        updated["incident_id"] = f"FLEET-M{machine_number:02d}-{incident_index:04d}-S{segment_index + 1:02d}"
        updated["start_time"] = segment_start.strftime("%Y-%m-%dT%H:%M:%S")
        updated["end_time"] = segment_end.strftime("%Y-%m-%dT%H:%M:%S")
        updated["duration_seconds"] = max(1, int((segment_end - segment_start).total_seconds()))
        updated["episode_index"] = segment_index + 1
        updated["episode_count"] = segment_count
        segments.append(updated)

    return segments


def _line_id_for_machine(machine_id: str) -> str:
    """Return line ID for a machine."""
    for machine in FLEET_MACHINES:
        if machine["machine_id"] == machine_id:
            return str(machine["line_id"])
    return "unknown"


def _display_name_for_machine(machine_id: str) -> str:
    """Return display name for a machine."""
    for machine in FLEET_MACHINES:
        if machine["machine_id"] == machine_id:
            return str(machine["display_name"])
    return machine_id


def _build_fleet_summary(
    processed: pd.DataFrame,
    incidents: list[dict[str, Any]],
    sensor_rows: int,
    incident_rows: int,
) -> dict[str, Any]:
    """Build a compact fleet summary."""
    machine_summaries: list[dict[str, Any]] = []

    for machine_id, group in processed.groupby("machine_id"):
        group = group.sort_values("timestamp")
        latest = group.iloc[-1]
        machine_incidents = [incident for incident in incidents if incident["machine_id"] == machine_id]

        machine_summaries.append(
            {
                "machine_id": machine_id,
                "line_id": _line_id_for_machine(str(machine_id)),
                "display_name": _display_name_for_machine(str(machine_id)),
                "rows": int(len(group)),
                "incident_count": int(len(machine_incidents)),
                "latest_timestamp": str(latest["timestamp"]),
                "latest_health_score": int(latest["health_score"]),
                "minimum_health_score": int(group["health_score"].min()),
                "latest_risk_level": str(latest["risk_level"]),
                "anomaly_rows": int((group["anomaly_score"] > 0).sum()),
                "suspected_faults": sorted(
                    {
                        str(incident["suspected_fault"])
                        for incident in machine_incidents
                        if incident.get("suspected_fault")
                    }
                ),
            }
        )

    machine_summaries = sorted(machine_summaries, key=lambda item: item["machine_id"])

    return {
        "fleet": {
            "machine_count": int(processed["machine_id"].nunique()),
            "sensor_rows": int(sensor_rows),
            "incident_rows": int(incident_rows),
            "time_start": str(processed["timestamp"].min()),
            "time_end": str(processed["timestamp"].max()),
            "incident_segmentation": {
                "enabled": True,
                "long_incident_threshold_seconds": SEGMENT_LONG_INCIDENTS_AFTER_SECONDS,
                "target_segment_seconds": TARGET_SEGMENT_SECONDS,
                "max_segments_per_incident": MAX_SEGMENTS_PER_INCIDENT,
            },
        },
        "machines": machine_summaries,
        "incidents": incidents,
    }


def _summary_to_markdown(summary: dict[str, Any]) -> str:
    """Convert fleet summary to Markdown."""
    lines = [
        "# TwinAgent AI Fleet Demo Summary",
        "",
        "## Fleet overview",
        "",
        f"- Machines: {summary['fleet']['machine_count']}",
        f"- Sensor rows: {summary['fleet']['sensor_rows']}",
        f"- Incidents: {summary['fleet']['incident_rows']}",
        f"- Time range: `{summary['fleet']['time_start']}` to `{summary['fleet']['time_end']}`",
        f"- Long incident segmentation: {summary['fleet']['incident_segmentation']}",
        "",
        "## Machine summary",
        "",
        "| Machine | Line | Rows | Incidents | Latest health | Min health | Latest risk | Suspected faults |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]

    for machine in summary["machines"]:
        lines.append(
            "| "
            f"{machine['machine_id']} | "
            f"{machine['line_id']} | "
            f"{machine['rows']} | "
            f"{machine['incident_count']} | "
            f"{machine['latest_health_score']} | "
            f"{machine['minimum_health_score']} | "
            f"{machine['latest_risk_level']} | "
            f"{', '.join(machine['suspected_faults']) or 'none'} |"
        )

    lines.extend(["", "## Incidents", ""])

    for incident in summary["incidents"]:
        episode = ""
        if int(incident.get("episode_count", 1)) > 1:
            episode = f" | episode {incident['episode_index']}/{incident['episode_count']}"
        lines.append(
            "- "
            f"`{incident['incident_id']}` | `{incident['machine_id']}` | "
            f"{incident['severity']} | {incident['suspected_fault']} | "
            f"`{incident['start_time']}` → `{incident['end_time']}`{episode}"
        )

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
