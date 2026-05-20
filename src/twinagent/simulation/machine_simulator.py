"""Synthetic conveyor-motor digital twin simulator for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from twinagent.simulation.fault_profiles import (
    FaultEvent,
    apply_fault_effects,
    highest_severity,
    load_fault_events,
)
from twinagent.simulation.sensor_models import SensorRange, clamp_value, sinusoidal_variation


@dataclass
class MachineSimulator:
    """Generate synthetic time-series data for a conveyor-motor digital twin."""

    config: dict[str, Any]

    def __post_init__(self) -> None:
        machine_config = self.config.get("machine", {})
        operation_config = self.config.get("operation", {})
        sensor_config = self.config.get("sensors", {})

        self.machine_id = str(machine_config.get("machine_id", "line1_motor1"))
        self.machine_type = str(machine_config.get("type", "conveyor_motor"))
        self.sampling_rate_hz = float(machine_config.get("sampling_rate_hz", 1))
        self.duration_minutes = float(machine_config.get("duration_minutes", 60))
        self.random_seed = int(machine_config.get("random_seed", 42))
        self.start_time = pd.Timestamp(machine_config.get("start_time", "2026-05-20T14:00:00"))

        if self.sampling_rate_hz <= 0:
            raise ValueError("machine.sampling_rate_hz must be greater than zero.")
        if self.duration_minutes <= 0:
            raise ValueError("machine.duration_minutes must be greater than zero.")

        self.operating_mode = str(operation_config.get("operating_mode", "production"))
        self.load_baseline_pct = float(operation_config.get("load_baseline_pct", 65))
        self.load_variation_pct = float(operation_config.get("load_variation_pct", 18))

        self.sensor_ranges = {
            name: SensorRange.from_config(name, values)
            for name, values in sensor_config.items()
        }
        self.fault_events = load_fault_events(self.config)

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> "MachineSimulator":
        """Create a simulator from a YAML configuration file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Machine config not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError(f"Machine config must be a YAML mapping: {path}")

        return cls(config=config)

    def simulate(self) -> pd.DataFrame:
        """Generate a complete synthetic sensor dataset.

        The random generator is reset for each simulation call so repeated runs
        with the same config produce identical data. This keeps tests, saved CSV
        files, and printed summaries reproducible.
        """
        rng = np.random.default_rng(self.random_seed)

        total_samples = int(self.duration_minutes * 60 * self.sampling_rate_hz)
        sample_period_seconds = 1.0 / self.sampling_rate_hz
        timestamps = pd.date_range(
            start=self.start_time,
            periods=total_samples,
            freq=pd.to_timedelta(sample_period_seconds, unit="s"),
        )

        rows: list[dict[str, float | str | pd.Timestamp]] = []

        for index, timestamp in enumerate(timestamps):
            elapsed_seconds = int(index * sample_period_seconds)
            row = self._simulate_normal_row(timestamp, elapsed_seconds, rng)

            active_faults = [
                fault for fault in self.fault_events if fault.is_active(elapsed_seconds)
            ]

            for fault in active_faults:
                apply_fault_effects(row, fault, elapsed_seconds, rng)

            row["fault_label"] = (
                "+".join(fault.fault_type for fault in active_faults)
                if active_faults
                else "normal"
            )
            row["fault_severity"] = highest_severity(active_faults)
            row["machine_state"] = self._infer_machine_state(row, active_faults)

            rows.append(row)

        dataframe = pd.DataFrame(rows)
        return self._finalize_dataframe(dataframe)

    def save_csv(self, output_path: str | Path) -> Path:
        """Generate the dataset and save it as a CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        dataframe = self.simulate()
        dataframe.to_csv(path, index=False)
        return path

    def _simulate_normal_row(
        self,
        timestamp: pd.Timestamp,
        elapsed_seconds: int,
        rng: np.random.Generator,
    ) -> dict[str, float | str | pd.Timestamp]:
        """Simulate one row of normal operating data before fault injection."""
        load_pct = (
            self.load_baseline_pct
            + sinusoidal_variation(elapsed_seconds, period_seconds=900, amplitude=self.load_variation_pct)
            + sinusoidal_variation(elapsed_seconds, period_seconds=240, amplitude=self.load_variation_pct / 3)
            + rng.normal(0.0, self._noise("load_pct", fallback=2.5))
        )
        load_pct = clamp_value(load_pct, 15.0, 98.0)

        ambient_temperature_c = (
            23.0
            + sinusoidal_variation(elapsed_seconds, period_seconds=3600, amplitude=2.0)
            + rng.normal(0.0, self._noise("ambient_temperature_c", fallback=0.3))
        )

        rpm = (
            1500.0
            - 1.6 * (load_pct - self.load_baseline_pct)
            + rng.normal(0.0, self._noise("rpm", fallback=12.0))
        )

        belt_speed_mps = (
            1.35
            + (rpm - 1500.0) / 850.0
            + rng.normal(0.0, self._noise("belt_speed_mps", fallback=0.02))
        )
        belt_speed_mps = clamp_value(belt_speed_mps, 0.35, 2.2)

        current_a = (
            4.4
            + 0.095 * load_pct
            + rng.normal(0.0, self._noise("current_a", fallback=0.35))
        )

        temperature_c = (
            38.0
            + 0.34 * load_pct
            + 0.4 * (ambient_temperature_c - 22.0)
            + sinusoidal_variation(elapsed_seconds, period_seconds=1800, amplitude=1.8)
            + rng.normal(0.0, self._noise("temperature_c", fallback=0.8))
        )

        vibration_mm_s = (
            0.18
            + 0.0065 * load_pct
            + abs(rng.normal(0.0, self._noise("vibration_mm_s", fallback=0.05)))
        )

        throughput_units_min = (
            belt_speed_mps * 78.0 * (load_pct / max(self.load_baseline_pct, 1.0))
            + rng.normal(0.0, self._noise("throughput_units_min", fallback=4.0))
        )
        throughput_units_min = max(0.0, throughput_units_min)

        return {
            "timestamp": timestamp,
            "machine_id": self.machine_id,
            "temperature_c": temperature_c,
            "vibration_mm_s": vibration_mm_s,
            "rpm": rpm,
            "current_a": current_a,
            "load_pct": load_pct,
            "belt_speed_mps": belt_speed_mps,
            "throughput_units_min": throughput_units_min,
            "ambient_temperature_c": ambient_temperature_c,
            "operating_mode": self.operating_mode,
            "machine_state": "normal",
            "fault_label": "normal",
            "fault_severity": "none",
        }

    def _noise(self, sensor_name: str, fallback: float) -> float:
        """Return configured noise for a sensor."""
        sensor = self.sensor_ranges.get(sensor_name)
        if sensor is None:
            return fallback
        return sensor.noise_std

    @staticmethod
    def _infer_machine_state(
        row: dict[str, float | str | pd.Timestamp],
        active_faults: list[FaultEvent],
    ) -> str:
        """Infer a human-readable machine state from sensor values and faults."""
        temperature = float(row["temperature_c"])
        vibration = float(row["vibration_mm_s"])
        current = float(row["current_a"])

        if temperature >= 92.0 or vibration >= 2.8 or current >= 15.0:
            return "critical"
        if temperature >= 82.0 or vibration >= 1.4 or current >= 13.0:
            return "warning"
        if active_faults:
            return "degraded"
        return "normal"

    @staticmethod
    def _finalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Apply stable column ordering and numeric rounding."""
        column_order = [
            "timestamp",
            "machine_id",
            "temperature_c",
            "vibration_mm_s",
            "rpm",
            "current_a",
            "load_pct",
            "belt_speed_mps",
            "throughput_units_min",
            "ambient_temperature_c",
            "operating_mode",
            "machine_state",
            "fault_label",
            "fault_severity",
        ]

        dataframe = dataframe[column_order].copy()

        numeric_precision = {
            "temperature_c": 2,
            "vibration_mm_s": 3,
            "rpm": 1,
            "current_a": 2,
            "load_pct": 2,
            "belt_speed_mps": 3,
            "throughput_units_min": 2,
            "ambient_temperature_c": 2,
        }

        for column, decimals in numeric_precision.items():
            dataframe[column] = dataframe[column].astype(float).round(decimals)

        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"]).dt.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        return dataframe
