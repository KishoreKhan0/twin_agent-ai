"""Incident grouping for TwinAgent AI anomaly outputs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class IncidentDetector:
    """Group anomaly rows into incident records."""

    min_duration_seconds: int = 20
    max_gap_seconds: int = 90

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "IncidentDetector":
        """Create an incident detector from the anomaly config."""
        grouping = config.get("detector", {}).get("incident_grouping", {})
        return cls(
            min_duration_seconds=int(grouping.get("min_duration_seconds", 20)),
            max_gap_seconds=int(grouping.get("max_gap_seconds", 90)),
        )

    def detect_incidents(self, dataframe: pd.DataFrame) -> list[dict[str, Any]]:
        """Group consecutive anomaly rows into incidents."""
        if dataframe.empty:
            return []
        if "is_anomaly" not in dataframe.columns:
            raise ValueError("Dataframe must include an is_anomaly column.")

        working = dataframe.copy()
        working["timestamp"] = pd.to_datetime(working["timestamp"])
        working = working.sort_values("timestamp").reset_index(drop=True)

        anomaly_rows = working[working["is_anomaly"]].copy()
        if anomaly_rows.empty:
            return []

        groups: list[pd.DataFrame] = []
        current_indices: list[int] = []
        previous_timestamp: pd.Timestamp | None = None

        for index, row in anomaly_rows.iterrows():
            timestamp = row["timestamp"]

            if previous_timestamp is None:
                current_indices = [index]
            else:
                gap_seconds = (timestamp - previous_timestamp).total_seconds()
                if gap_seconds <= self.max_gap_seconds:
                    current_indices.append(index)
                else:
                    groups.append(anomaly_rows.loc[current_indices].copy())
                    current_indices = [index]

            previous_timestamp = timestamp

        if current_indices:
            groups.append(anomaly_rows.loc[current_indices].copy())

        incidents: list[dict[str, Any]] = []
        for incident_number, group in enumerate(groups, start=1):
            incident = self._build_incident(incident_number, group)
            if incident["duration_seconds"] >= self.min_duration_seconds:
                incidents.append(incident)

        return incidents

    def _build_incident(self, incident_number: int, group: pd.DataFrame) -> dict[str, Any]:
        """Build one incident dictionary from a grouped anomaly dataframe."""
        start_time = group["timestamp"].min()
        end_time = group["timestamp"].max()
        duration_seconds = int((end_time - start_time).total_seconds()) + 1

        severity = self._highest_severity(group["anomaly_severity"].tolist())
        contributing_sensors = self._merge_contributors(group["contributing_sensors"].tolist())
        suspected_fault = self._infer_group_fault(group, contributing_sensors)
        evidence = self._build_evidence(group, contributing_sensors)

        return {
            "incident_id": f"INC-{incident_number:04d}",
            "machine_id": str(group["machine_id"].iloc[0]),
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_seconds": duration_seconds,
            "severity": severity,
            "suspected_fault": suspected_fault,
            "max_anomaly_score": round(float(group["anomaly_score"].max()), 4),
            "mean_anomaly_score": round(float(group["anomaly_score"].mean()), 4),
            "contributing_sensors": contributing_sensors,
            "evidence": evidence,
        }

    @staticmethod
    def _highest_severity(severities: list[str]) -> str:
        """Return the highest severity found in a group."""
        rank = {"none": 0, "low": 1, "medium": 2, "high": 3}
        return max(severities, key=lambda value: rank.get(value, 0))

    def _infer_group_fault(self, group: pd.DataFrame, contributors: list[str]) -> str:
        """Infer the dominant incident-level fault from sensor-score patterns."""
        max_scores = {
            "temperature_c": self._max_score(group, "temperature_c"),
            "vibration_mm_s": self._max_score(group, "vibration_mm_s"),
            "current_a": self._max_score(group, "current_a"),
            "throughput_units_min": self._max_score(group, "throughput_units_min"),
        }

        if (
            max_scores["vibration_mm_s"] >= 0.55
            and max_scores["temperature_c"] >= 0.55
        ):
            return "bearing_wear"

        if (
            max_scores["vibration_mm_s"] >= 0.55
            and max_scores["throughput_units_min"] >= 0.55
            and max_scores["temperature_c"] < 0.55
        ):
            return "belt_misalignment"

        if (
            max_scores["temperature_c"] >= 0.55
            and max_scores["vibration_mm_s"] < 0.55
        ):
            return "overheating"

        if (
            max_scores["current_a"] >= 0.55
            and max_scores["temperature_c"] >= 0.35
        ):
            return "motor_overload"

        return self._most_common_non_normal(group["suspected_fault"].tolist(), contributors)

    @staticmethod
    def _max_score(group: pd.DataFrame, sensor_name: str) -> float:
        """Return max anomaly score for a sensor within a group."""
        column = f"{sensor_name}_anomaly_score"
        if column not in group.columns:
            return 0.0
        return float(group[column].max())

    @staticmethod
    def _most_common_non_normal(values: list[str], contributors: list[str]) -> str:
        """Return the most common suspected fault, ignoring normal labels."""
        filtered = [
            value
            for value in values
            if isinstance(value, str) and value and value != "normal"
        ]
        if filtered:
            return Counter(filtered).most_common(1)[0][0]

        if contributors:
            return f"{contributors[0]}_anomaly"
        return "unknown_anomaly"

    @staticmethod
    def _merge_contributors(contributor_values: list[str]) -> list[str]:
        """Merge semicolon-separated contributor values into a sorted list."""
        contributors: set[str] = set()

        for value in contributor_values:
            if not isinstance(value, str) or not value:
                continue
            contributors.update(part for part in value.split(";") if part)

        return sorted(contributors)

    @staticmethod
    def _build_evidence(group: pd.DataFrame, contributors: list[str]) -> dict[str, str]:
        """Build concise numeric evidence for each contributing sensor."""
        evidence: dict[str, str] = {}

        for sensor in contributors:
            if sensor not in group.columns:
                continue

            sensor_values = group[sensor].astype(float)
            sensor_score_column = f"{sensor}_anomaly_score"

            max_value = sensor_values.max()
            min_value = sensor_values.min()

            if sensor_score_column in group.columns:
                max_score = float(group[sensor_score_column].max())
                evidence[sensor] = (
                    f"value range {min_value:.2f} to {max_value:.2f}; "
                    f"max sensor anomaly score {max_score:.2f}"
                )
            else:
                evidence[sensor] = f"value range {min_value:.2f} to {max_value:.2f}"

        return evidence
