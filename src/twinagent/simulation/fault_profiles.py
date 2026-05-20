"""Fault profile definitions for the synthetic conveyor-motor digital twin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from twinagent.simulation.sensor_models import clamp_value


SEVERITY_FACTORS: dict[str, float] = {
    "low": 0.65,
    "medium": 1.0,
    "high": 1.35,
}

SEVERITY_RANK: dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


@dataclass(frozen=True)
class FaultEvent:
    """A configured fault event with a start time and duration."""

    fault_type: str
    start_offset_seconds: int
    duration_seconds: int
    severity: str

    @property
    def end_offset_seconds(self) -> int:
        """Return the exclusive end time of the fault in elapsed seconds."""
        return self.start_offset_seconds + self.duration_seconds

    def is_active(self, elapsed_seconds: int) -> bool:
        """Return True if the fault is active at the given elapsed second."""
        return self.start_offset_seconds <= elapsed_seconds < self.end_offset_seconds

    def progress(self, elapsed_seconds: int) -> float:
        """Return fault progress from 0.0 to 1.0 during the active window."""
        if not self.is_active(elapsed_seconds):
            return 0.0
        if self.duration_seconds <= 0:
            return 1.0
        return clamp_value(
            (elapsed_seconds - self.start_offset_seconds) / self.duration_seconds,
            0.0,
            1.0,
        )


def parse_hhmmss_to_seconds(value: str) -> int:
    """Parse a HH:MM:SS offset string into seconds."""
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected HH:MM:SS time offset, got {value!r}.")

    hours, minutes, seconds = (int(part) for part in parts)
    if minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60 or hours < 0:
        raise ValueError(f"Invalid HH:MM:SS time offset: {value!r}.")

    return (hours * 3600) + (minutes * 60) + seconds


def load_fault_events(config: dict[str, Any]) -> list[FaultEvent]:
    """Load fault events from the machine configuration."""
    fault_events: list[FaultEvent] = []

    for raw_fault in config.get("faults", []):
        fault_type = str(raw_fault["type"])
        severity = str(raw_fault.get("severity", "medium")).lower()

        if severity not in SEVERITY_FACTORS:
            raise ValueError(
                f"Fault {fault_type!r} has invalid severity {severity!r}. "
                f"Expected one of {sorted(SEVERITY_FACTORS)}."
            )

        duration_minutes = float(raw_fault.get("duration_minutes", 5))
        if duration_minutes <= 0:
            raise ValueError(f"Fault {fault_type!r} duration_minutes must be positive.")

        fault_events.append(
            FaultEvent(
                fault_type=fault_type,
                start_offset_seconds=parse_hhmmss_to_seconds(str(raw_fault["start_time"])),
                duration_seconds=int(duration_minutes * 60),
                severity=severity,
            )
        )

    return sorted(fault_events, key=lambda event: event.start_offset_seconds)


def highest_severity(active_faults: list[FaultEvent]) -> str:
    """Return the highest severity among active faults."""
    if not active_faults:
        return "none"
    return max(active_faults, key=lambda fault: SEVERITY_RANK[fault.severity]).severity


def apply_fault_effects(
    row: dict[str, float | str],
    fault: FaultEvent,
    elapsed_seconds: int,
    rng: np.random.Generator,
) -> None:
    """Modify one simulated sensor row in-place according to a fault profile.

    The profiles are intentionally interpretable rather than physically exact.
    They are designed to create realistic-looking sensor patterns for anomaly
    detection, RAG explanations, and dashboard visualization.
    """
    progress = fault.progress(elapsed_seconds)
    severity_factor = SEVERITY_FACTORS[fault.severity]

    if fault.fault_type == "bearing_wear":
        row["vibration_mm_s"] = float(row["vibration_mm_s"]) + (0.35 + 1.8 * progress) * severity_factor
        row["temperature_c"] = float(row["temperature_c"]) + (1.5 + 10.0 * progress) * severity_factor
        row["current_a"] = float(row["current_a"]) + (0.15 + 1.0 * progress) * severity_factor
        row["rpm"] = float(row["rpm"]) + rng.normal(0.0, 18.0 + 25.0 * progress)

    elif fault.fault_type == "overheating":
        row["temperature_c"] = float(row["temperature_c"]) + (5.0 + 26.0 * progress) * severity_factor
        row["current_a"] = float(row["current_a"]) + (0.25 + 0.6 * progress) * severity_factor

    elif fault.fault_type == "belt_misalignment":
        row["vibration_mm_s"] = float(row["vibration_mm_s"]) + (0.45 + 1.1 * progress) * severity_factor
        row["throughput_units_min"] = float(row["throughput_units_min"]) * (1.0 - 0.22 * progress)
        row["belt_speed_mps"] = float(row["belt_speed_mps"]) * (1.0 - 0.12 * progress)
        row["current_a"] = float(row["current_a"]) + (0.2 + 0.7 * progress) * severity_factor

    elif fault.fault_type == "motor_overload":
        row["current_a"] = float(row["current_a"]) + (2.0 + 4.0 * progress) * severity_factor
        row["temperature_c"] = float(row["temperature_c"]) + (3.0 + 12.0 * progress) * severity_factor
        row["rpm"] = float(row["rpm"]) - (35.0 + 120.0 * progress) * severity_factor

    elif fault.fault_type == "sensor_drift":
        row["temperature_c"] = float(row["temperature_c"]) + (1.0 + 13.0 * progress) * severity_factor

    elif fault.fault_type == "cooling_failure":
        row["temperature_c"] = float(row["temperature_c"]) + (4.0 + 22.0 * progress) * severity_factor

    else:
        raise ValueError(f"Unsupported fault type: {fault.fault_type!r}")
