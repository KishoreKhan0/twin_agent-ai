"""Interpretable anomaly detection for TwinAgent AI sensor data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


@dataclass
class AnomalyDetector:
    """Detect anomalies using directional thresholds and rolling z-score columns.

    The MVP intentionally uses conservative threshold-based scoring to avoid
    flagging normal load-driven operating variation as an anomaly. Rolling
    z-scores are still computed and stored for analysis, but the current config
    keeps their contribution disabled by setting very high z thresholds.
    """

    config: dict[str, Any]

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> "AnomalyDetector":
        """Create an anomaly detector from a YAML configuration file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Anomaly config not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError(f"Anomaly config must be a YAML mapping: {path}")

        return cls(config=config)

    def detect(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of the dataframe with anomaly columns added."""
        if dataframe.empty:
            raise ValueError("Cannot run anomaly detection on an empty dataframe.")

        result = dataframe.copy()
        result["timestamp"] = pd.to_datetime(result["timestamp"])

        sensor_configs = self.config.get("sensors", {})
        if not sensor_configs:
            raise ValueError("Anomaly config must define at least one sensor.")

        sensor_score_columns: list[str] = []

        for sensor_name, sensor_config in sensor_configs.items():
            if sensor_name not in result.columns:
                continue

            threshold_score = self._threshold_score(result[sensor_name], sensor_config)
            z_values, z_score = self._rolling_z_score(result[sensor_name], sensor_config)

            score_column = f"{sensor_name}_anomaly_score"
            z_column = f"{sensor_name}_rolling_z"

            result[score_column] = np.maximum(
                threshold_score.to_numpy(),
                z_score.to_numpy(),
            ).round(4)
            result[z_column] = z_values.round(4)

            sensor_score_columns.append(score_column)

        if not sensor_score_columns:
            raise ValueError("No configured sensors were found in the dataframe.")

        result["anomaly_score"] = self._combined_score(result, sensor_score_columns).round(4)
        result["is_anomaly"] = result["anomaly_score"] >= self._threshold("low")
        result["anomaly_severity"] = result["anomaly_score"].apply(self._severity_from_score)
        result["contributing_sensors"] = result.apply(
            lambda row: self._contributing_sensors(row, sensor_score_columns),
            axis=1,
        )
        result["suspected_fault"] = result.apply(self._suspected_fault, axis=1)

        result["timestamp"] = result["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        return result

    def _threshold(self, level: str) -> float:
        """Return configured anomaly threshold for a severity level."""
        thresholds = self.config.get("detector", {}).get("anomaly_thresholds", {})
        defaults = {"low": 0.25, "medium": 0.45, "high": 0.70}
        return float(thresholds.get(level, defaults[level]))

    @staticmethod
    def _threshold_score(series: pd.Series, sensor_config: dict[str, Any]) -> pd.Series:
        """Compute directional score from configured warning/high bounds.

        Supported directions:
        - upper: anomaly when value is too high
        - lower: anomaly when value is too low
        - outside: anomaly when value is outside a low/high operating band
        """
        values = series.astype(float)
        score = pd.Series(0.0, index=series.index)

        direction = str(sensor_config.get("direction", "upper")).lower()

        warning_min = sensor_config.get("warning_min")
        high_min = sensor_config.get("high_min")
        warning_max = sensor_config.get("warning_max")
        high_max = sensor_config.get("high_max")

        if direction == "upper":
            if warning_min is not None:
                score = score.mask(values >= float(warning_min), 0.55)
            if high_min is not None:
                score = score.mask(values >= float(high_min), 0.95)

        elif direction == "lower":
            if warning_min is not None:
                score = score.mask(values <= float(warning_min), 0.55)
            if high_min is not None:
                score = score.mask(values <= float(high_min), 0.95)

        elif direction == "outside":
            if warning_min is not None:
                score = score.mask(values <= float(warning_min), 0.55)
            if warning_max is not None:
                score = score.mask(values >= float(warning_max), 0.55)
            if high_min is not None:
                score = score.mask(values <= float(high_min), 0.95)
            if high_max is not None:
                score = score.mask(values >= float(high_max), 0.95)

        else:
            raise ValueError(
                f"Unsupported threshold direction {direction!r}. "
                "Expected one of: upper, lower, outside."
            )

        return score.clip(0.0, 1.0)

    def _rolling_z_score(
        self,
        series: pd.Series,
        sensor_config: dict[str, Any],
    ) -> tuple[pd.Series, pd.Series]:
        """Compute rolling z-values and a normalized z-score anomaly contribution."""
        detector_config = self.config.get("detector", {})
        window = int(detector_config.get("rolling_window_samples", 300))
        min_periods = int(detector_config.get("min_periods", 30))

        values = series.astype(float)
        rolling_mean = values.rolling(window=window, min_periods=min_periods).mean()
        rolling_std = values.rolling(window=window, min_periods=min_periods).std(ddof=0)
        rolling_std = rolling_std.replace(0.0, np.nan)

        z_values = ((values - rolling_mean) / rolling_std).fillna(0.0)
        abs_z = z_values.abs()

        z_warning = float(sensor_config.get("z_warning", 2.5))
        z_high = float(sensor_config.get("z_high", 4.0))

        if z_high <= z_warning:
            raise ValueError("z_high must be greater than z_warning.")

        z_score = ((abs_z - z_warning) / (z_high - z_warning)).clip(0.0, 1.0)
        return z_values, z_score

    def _combined_score(self, dataframe: pd.DataFrame, sensor_score_columns: list[str]) -> pd.Series:
        """Combine sensor scores into one weighted anomaly score."""
        sensor_configs = self.config.get("sensors", {})

        weighted_sum = pd.Series(0.0, index=dataframe.index)
        total_weight = 0.0

        for score_column in sensor_score_columns:
            sensor_name = score_column.replace("_anomaly_score", "")
            weight = float(sensor_configs.get(sensor_name, {}).get("weight", 1.0))
            weighted_sum += dataframe[score_column].astype(float) * weight
            total_weight += weight

        weighted_average = weighted_sum / max(total_weight, 1e-9)
        max_sensor_score = dataframe[sensor_score_columns].max(axis=1)

        # Blend average system risk with peak single-sensor risk.
        return ((0.55 * weighted_average) + (0.45 * max_sensor_score)).clip(0.0, 1.0)

    def _severity_from_score(self, score: float) -> str:
        """Convert anomaly score into severity label."""
        if score >= self._threshold("high"):
            return "high"
        if score >= self._threshold("medium"):
            return "medium"
        if score >= self._threshold("low"):
            return "low"
        return "none"

    @staticmethod
    def _contributing_sensors(row: pd.Series, sensor_score_columns: list[str]) -> str:
        """Return a semicolon-separated list of sensors contributing to an anomaly."""
        contributors: list[str] = []

        for score_column in sensor_score_columns:
            score = float(row[score_column])
            if score >= 0.35:
                contributors.append(score_column.replace("_anomaly_score", ""))

        return ";".join(contributors)

    @staticmethod
    def _suspected_fault(row: pd.Series) -> str:
        """Infer a suspected fault type from interpretable sensor patterns."""
        if not bool(row["is_anomaly"]):
            return "normal"

        temperature_score = float(row.get("temperature_c_anomaly_score", 0.0))
        vibration_score = float(row.get("vibration_mm_s_anomaly_score", 0.0))
        current_score = float(row.get("current_a_anomaly_score", 0.0))
        throughput_score = float(row.get("throughput_units_min_anomaly_score", 0.0))

        if vibration_score >= 0.55 and throughput_score >= 0.35:
            return "belt_misalignment"
        if vibration_score >= 0.55 and temperature_score >= 0.35:
            return "bearing_wear"
        if temperature_score >= 0.55 and current_score < 0.55:
            return "overheating"
        if current_score >= 0.55 and temperature_score >= 0.35:
            return "motor_overload"
        if temperature_score >= 0.35:
            return "thermal_anomaly"
        if vibration_score >= 0.35:
            return "vibration_anomaly"
        if current_score >= 0.35:
            return "current_anomaly"
        if throughput_score >= 0.35:
            return "throughput_anomaly"
        return "unknown_anomaly"
