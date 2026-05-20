"""Predictive-maintenance recommendation logic for TwinAgent AI.

The recommendations are rule-based and evidence-grounded. They are designed for
a synthetic digital-twin prototype and should be described as maintenance
prioritization logic, not as certified predictive-maintenance output.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PredictiveMaintenanceAdvisor:
    """Add maintenance urgency and recommendation columns to anomaly outputs."""

    def add_maintenance_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return a copy with maintenance_urgency and maintenance_recommendation columns."""
        if dataframe.empty:
            raise ValueError("Cannot generate maintenance advice for an empty dataframe.")
        if "health_score" not in dataframe.columns:
            raise ValueError("Dataframe must include health_score before maintenance advice.")
        if "risk_level" not in dataframe.columns:
            raise ValueError("Dataframe must include risk_level before maintenance advice.")

        result = dataframe.copy()
        result["maintenance_urgency"] = result.apply(self._urgency_for_row, axis=1)
        result["maintenance_recommendation"] = result.apply(self._recommendation_for_row, axis=1)
        return result

    @staticmethod
    def _urgency_for_row(row: pd.Series) -> str:
        """Assign a maintenance urgency label for one row."""
        health_score = int(row["health_score"])
        severity = str(row.get("anomaly_severity", "none")).lower()
        risk_level = str(row.get("risk_level", "healthy")).lower()

        if health_score < 35 or severity == "high" or risk_level == "critical":
            return "stop_and_inspect"
        if health_score < 55 or severity == "medium" or risk_level == "high":
            return "inspect_within_24h"
        if health_score < 70 or severity == "low" or risk_level == "medium":
            return "inspect_within_48h"
        if health_score < 85 or risk_level == "watch":
            return "monitor"
        return "normal_operation"

    @staticmethod
    def _recommendation_for_row(row: pd.Series) -> str:
        """Generate a concise maintenance recommendation for one row."""
        urgency = str(row.get("maintenance_urgency", "normal_operation"))
        suspected_fault = str(row.get("suspected_fault", "normal"))
        contributors = PredictiveMaintenanceAdvisor._parse_contributors(
            row.get("contributing_sensors", "")
        )

        if urgency == "normal_operation":
            return "Continue normal operation and routine monitoring."

        if suspected_fault == "bearing_wear":
            return (
                "Inspect bearing housing, lubrication condition, and vibration trend; "
                "reduce load if vibration or temperature continues rising."
            )

        if suspected_fault == "belt_misalignment":
            return (
                "Inspect belt alignment, tension, pulley condition, and throughput drop; "
                "verify conveyor tracking before returning to full load."
            )

        if suspected_fault in {"overheating", "thermal_anomaly"}:
            return (
                "Check cooling airflow, ambient temperature, motor surface temperature, "
                "and load level; reduce load until temperature stabilizes."
            )

        if suspected_fault in {"motor_overload", "current_anomaly"}:
            return (
                "Check motor current draw, load condition, drive settings, and possible "
                "mechanical blockage before continuing operation."
            )

        if "vibration_mm_s" in contributors:
            return "Inspect mechanical alignment, bearings, fasteners, and vibration trend."

        if "temperature_c" in contributors:
            return "Inspect cooling path, load profile, and temperature trend."

        if "current_a" in contributors:
            return "Inspect motor load, electrical draw, and drive configuration."

        return "Review anomaly evidence and schedule technician inspection."

    @staticmethod
    def _parse_contributors(value: object) -> list[str]:
        """Parse semicolon-separated contributor strings into a list."""
        if not isinstance(value, str) or not value:
            return []
        return [part for part in value.split(";") if part]
