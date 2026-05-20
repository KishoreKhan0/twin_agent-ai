"""Reusable sensor modeling utilities for the TwinAgent AI simulator."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SensorRange:
    """Normal operating range and noise settings for one sensor."""

    name: str
    normal_min: float
    normal_max: float
    noise_std: float

    @classmethod
    def from_config(cls, name: str, config: dict) -> "SensorRange":
        """Create a sensor range from a YAML sensor config block."""
        normal_range = config.get("normal_range")
        if not isinstance(normal_range, list) or len(normal_range) != 2:
            raise ValueError(f"Sensor {name!r} must define normal_range as [min, max].")

        return cls(
            name=name,
            normal_min=float(normal_range[0]),
            normal_max=float(normal_range[1]),
            noise_std=float(config.get("noise_std", 0.0)),
        )

    def clamp(self, value: float) -> float:
        """Clamp a value to the configured normal range."""
        return float(np.clip(value, self.normal_min, self.normal_max))

    def add_noise(self, value: float, rng: np.random.Generator) -> float:
        """Add Gaussian sensor noise to a value."""
        if self.noise_std <= 0:
            return float(value)
        return float(value + rng.normal(0.0, self.noise_std))


def clamp_value(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value to a given range."""
    return float(np.clip(value, min_value, max_value))


def sinusoidal_variation(
    elapsed_seconds: float,
    period_seconds: float,
    amplitude: float,
    phase: float = 0.0,
) -> float:
    """Return a smooth sinusoidal variation for synthetic operating patterns."""
    if period_seconds <= 0:
        raise ValueError("period_seconds must be greater than zero.")
    return float(amplitude * np.sin((2.0 * np.pi * elapsed_seconds / period_seconds) + phase))
