"""Tool layer for the TwinAgent AI copilot.

These tools provide the agentic layer with controlled access to project data:
incidents, processed sensor windows, anomaly summaries, maintenance advice, and
retrieved engineering documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

import pandas as pd

from twinagent.rag import RagRetriever, RetrievalResult


SENSOR_COLUMNS = [
    "temperature_c",
    "vibration_mm_s",
    "rpm",
    "current_a",
    "load_pct",
    "belt_speed_mps",
    "throughput_units_min",
    "ambient_temperature_c",
]


@dataclass
class TwinAgentTools:
    """Collection of deterministic tools used by the TwinAgent copilot."""

    processed_data_path: Path
    incidents_path: Path
    rag_config_path: Path
    project_root: Path

    _dataframe_cache: pd.DataFrame | None = field(default=None, init=False, repr=False)
    _incidents_cache: list[dict[str, Any]] | None = field(default=None, init=False, repr=False)
    _retriever_cache: RagRetriever | None = field(default=None, init=False, repr=False)

    def load_processed_data(self) -> pd.DataFrame:
        """Load processed sensor data with anomaly and health columns."""
        if self._dataframe_cache is None:
            if not self.processed_data_path.exists():
                raise FileNotFoundError(
                    f"Processed data file not found: {self.processed_data_path}. "
                    "Run python scripts\\run_anomaly_detection.py first."
                )

            dataframe = pd.read_csv(self.processed_data_path)
            required_columns = {
                "timestamp",
                "machine_id",
                "anomaly_score",
                "is_anomaly",
                "anomaly_severity",
                "health_score",
                "risk_level",
                "maintenance_urgency",
                "maintenance_recommendation",
            }
            missing = required_columns - set(dataframe.columns)
            if missing:
                raise ValueError(
                    "Processed data is missing required columns: "
                    + ", ".join(sorted(missing))
                )

            dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
            self._dataframe_cache = dataframe

        return self._dataframe_cache.copy()

    def load_incidents(self) -> list[dict[str, Any]]:
        """Load incident records from JSON."""
        if self._incidents_cache is None:
            if not self.incidents_path.exists():
                raise FileNotFoundError(
                    f"Incidents file not found: {self.incidents_path}. "
                    "Run python scripts\\run_anomaly_detection.py first."
                )

            with self.incidents_path.open("r", encoding="utf-8") as file:
                incidents = json.load(file)

            if not isinstance(incidents, list):
                raise ValueError("Incidents JSON must contain a list of incident objects.")

            self._incidents_cache = incidents

        return list(self._incidents_cache)

    def list_recent_incidents(
        self,
        machine_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """List recent incidents, optionally filtered by machine."""
        incidents = self.load_incidents()

        if machine_id is not None:
            incidents = [
                incident for incident in incidents if incident.get("machine_id") == machine_id
            ]

        incidents = sorted(incidents, key=lambda item: str(item.get("start_time", "")), reverse=True)
        return incidents[:limit]

    def get_incident(self, incident_id: str) -> dict[str, Any]:
        """Return one incident by ID."""
        for incident in self.load_incidents():
            if incident.get("incident_id") == incident_id:
                return dict(incident)

        raise ValueError(f"Incident not found: {incident_id}")

    def query_sensor_window(
        self,
        machine_id: str,
        start_time: str,
        end_time: str,
    ) -> pd.DataFrame:
        """Query processed sensor rows for a machine and time window."""
        dataframe = self.load_processed_data()

        start = pd.Timestamp(start_time)
        end = pd.Timestamp(end_time)

        window = dataframe[
            (dataframe["machine_id"] == machine_id)
            & (dataframe["timestamp"] >= start)
            & (dataframe["timestamp"] <= end)
        ].copy()

        if window.empty:
            raise ValueError(
                f"No sensor data found for {machine_id} between {start_time} and {end_time}."
            )

        return window

    def summarize_sensor_window(
        self,
        machine_id: str,
        start_time: str,
        end_time: str,
        contributing_sensors: list[str] | None = None,
    ) -> dict[str, Any]:
        """Summarize sensor and maintenance evidence for a time window."""
        window = self.query_sensor_window(machine_id, start_time, end_time)
        sensors = contributing_sensors or [
            sensor for sensor in SENSOR_COLUMNS if sensor in window.columns
        ]

        sensor_summary: dict[str, dict[str, float]] = {}
        for sensor in sensors:
            if sensor not in window.columns:
                continue

            values = window[sensor].astype(float)
            sensor_summary[sensor] = {
                "min": round(float(values.min()), 3),
                "max": round(float(values.max()), 3),
                "mean": round(float(values.mean()), 3),
                "start": round(float(values.iloc[0]), 3),
                "end": round(float(values.iloc[-1]), 3),
                "change": round(float(values.iloc[-1] - values.iloc[0]), 3),
            }

        latest_row = window.iloc[-1]
        return {
            "rows": int(len(window)),
            "time_range": {
                "start": window["timestamp"].iloc[0].strftime("%Y-%m-%dT%H:%M:%S"),
                "end": window["timestamp"].iloc[-1].strftime("%Y-%m-%dT%H:%M:%S"),
            },
            "max_anomaly_score": round(float(window["anomaly_score"].max()), 4),
            "mean_anomaly_score": round(float(window["anomaly_score"].mean()), 4),
            "min_health_score": int(window["health_score"].min()),
            "latest_health_score": int(latest_row["health_score"]),
            "latest_risk_level": str(latest_row["risk_level"]),
            "latest_maintenance_urgency": str(latest_row["maintenance_urgency"]),
            "latest_maintenance_recommendation": str(latest_row["maintenance_recommendation"]),
            "machine_state_counts": window["machine_state"].value_counts().to_dict()
            if "machine_state" in window.columns
            else {},
            "risk_level_counts": window["risk_level"].value_counts().to_dict(),
            "maintenance_urgency_counts": window["maintenance_urgency"].value_counts().to_dict(),
            "sensor_summary": sensor_summary,
        }

    def retrieve_knowledge(self, query: str, top_k: int = 4) -> list[RetrievalResult]:
        """Retrieve relevant engineering-document chunks."""
        if self._retriever_cache is None:
            self._retriever_cache = RagRetriever.from_config_file(
                self.rag_config_path,
                project_root=self.project_root,
            )

        return self._retriever_cache.retrieve(query=query, top_k=top_k)

    def generate_maintenance_checklist(
        self,
        suspected_fault: str,
        severity: str,
    ) -> list[str]:
        """Generate a practical checklist from suspected fault and severity."""
        suspected_fault = suspected_fault.lower()
        severity = severity.lower()

        checklist: list[str] = []

        if severity == "high":
            checklist.append("Reduce load or stop operation if the machine remains critical.")
        elif severity == "medium":
            checklist.append("Schedule technician inspection and keep close monitoring enabled.")
        else:
            checklist.append("Continue monitoring and compare the trend against normal operation.")

        if suspected_fault == "bearing_wear":
            checklist.extend(
                [
                    "Inspect bearing housing for heat, noise, and mechanical play.",
                    "Check lubrication condition and bearing seals.",
                    "Compare vibration and temperature trends before restarting at full load.",
                ]
            )
        elif suspected_fault == "belt_misalignment":
            checklist.extend(
                [
                    "Inspect belt tracking, pulley alignment, and belt edge wear.",
                    "Verify belt tension and check for material obstruction.",
                    "Confirm throughput and belt speed recover after adjustment.",
                ]
            )
        elif suspected_fault in {"overheating", "thermal_anomaly"}:
            checklist.extend(
                [
                    "Inspect cooling airflow and ventilation near the motor housing.",
                    "Check whether high load or ambient temperature contributed to the event.",
                    "Restart at reduced load and verify temperature stabilizes.",
                ]
            )
        elif suspected_fault in {"motor_overload", "current_anomaly"}:
            checklist.extend(
                [
                    "Check motor current draw and drive settings.",
                    "Inspect for blocked rollers or excessive payload.",
                    "Verify RPM and current return to expected range under reduced load.",
                ]
            )
        else:
            checklist.extend(
                [
                    "Review the incident evidence and contributing sensors.",
                    "Inspect the affected mechanical and electrical components.",
                    "Record technician findings to improve future diagnosis.",
                ]
            )

        return checklist
