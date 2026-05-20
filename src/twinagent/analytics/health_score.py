"""Health-score calculation for TwinAgent AI.

The health score is an interpretable proxy, not a real certified remaining-life
model. It converts anomaly evidence, machine state, and sensor stress into a
0-100 score that is useful for dashboarding and maintenance prioritization.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class HealthScoreCalculator:
    """Calculate machine health score and risk level from anomaly outputs."""

    min_health_score: int = 5
    max_health_score: int = 100

    def add_health_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of the dataframe with health_score and risk_level columns."""
        if dataframe.empty:
            raise ValueError("Cannot calculate health score for an empty dataframe.")
        if "anomaly_score" not in dataframe.columns:
            raise ValueError("Dataframe must include anomaly_score before health scoring.")

        result = dataframe.copy()

        severity_risk = result.get("anomaly_severity", pd.Series("none", index=result.index)).map(
            self._severity_to_risk
        )
        state_risk = result.get("machine_state", pd.Series("normal", index=result.index)).map(
            self._machine_state_to_risk
        )

        severity_risk = severity_risk.fillna(0.0).astype(float)
        state_risk = state_risk.fillna(0.0).astype(float)
        anomaly_risk = result["anomaly_score"].fillna(0.0).astype(float).clip(0.0, 1.0)

        sensor_stress = self._sensor_stress(result)

        total_risk = (
            0.58 * anomaly_risk
            + 0.22 * severity_risk
            + 0.12 * state_risk
            + 0.08 * sensor_stress
        ).clip(0.0, 1.0)

        health_score = self.max_health_score - (total_risk * 90.0)
        result["health_score"] = (
            health_score.clip(self.min_health_score, self.max_health_score).round().astype(int)
        )
        result["risk_level"] = result["health_score"].apply(self._risk_level_from_health)

        return result

    @staticmethod
    def _severity_to_risk(severity: object) -> float:
        """Map anomaly severity to normalized risk."""
        mapping = {
            "none": 0.0,
            "low": 0.25,
            "medium": 0.55,
            "high": 0.85,
        }
        return mapping.get(str(severity).lower(), 0.0)

    @staticmethod
    def _machine_state_to_risk(machine_state: object) -> float:
        """Map machine state to normalized risk."""
        mapping = {
            "normal": 0.0,
            "degraded": 0.35,
            "warning": 0.60,
            "critical": 0.90,
        }
        return mapping.get(str(machine_state).lower(), 0.0)

    @staticmethod
    def _sensor_stress(dataframe: pd.DataFrame) -> pd.Series:
        """Estimate stress using normalized industrial sensor values.

        The values are intentionally approximate and interpretable. They are not
        meant to model real equipment physics.
        """
        stress = pd.Series(0.0, index=dataframe.index)

        if "temperature_c" in dataframe.columns:
            temperature_stress = ((dataframe["temperature_c"].astype(float) - 75.0) / 25.0).clip(
                0.0,
                1.0,
            )
            stress = stress.combine(temperature_stress, max)

        if "vibration_mm_s" in dataframe.columns:
            vibration_stress = ((dataframe["vibration_mm_s"].astype(float) - 0.8) / 2.2).clip(
                0.0,
                1.0,
            )
            stress = stress.combine(vibration_stress, max)

        if "current_a" in dataframe.columns:
            current_stress = ((dataframe["current_a"].astype(float) - 12.0) / 4.0).clip(
                0.0,
                1.0,
            )
            stress = stress.combine(current_stress, max)

        return stress.fillna(0.0).clip(0.0, 1.0)

    @staticmethod
    def _risk_level_from_health(health_score: int) -> str:
        """Convert health score into a dashboard-friendly risk level."""
        if health_score >= 85:
            return "healthy"
        if health_score >= 70:
            return "watch"
        if health_score >= 55:
            return "medium"
        if health_score >= 35:
            return "high"
        return "critical"
