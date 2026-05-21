"""MQTT message schema helpers for TwinAgent AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any


SENSOR_TOPIC_PREFIX = "factory/line1"


@dataclass(frozen=True)
class SensorMessage:
    """A single MQTT-compatible sensor message."""

    timestamp: str
    machine_id: str
    sensor_name: str
    value: float | str | int | bool
    unit: str
    operating_mode: str
    machine_state: str
    fault_label: str
    anomaly_score: float | None = None
    health_score: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the message to a dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize the message as compact JSON."""
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "SensorMessage":
        """Deserialize a message from JSON."""
        data = json.loads(payload)
        return cls(**data)


def topic_for_sensor(machine_id: str, sensor_name: str, prefix: str = SENSOR_TOPIC_PREFIX) -> str:
    """Build a stable MQTT topic for one machine sensor."""
    clean_machine_id = _clean_topic_part(machine_id)
    clean_sensor_name = _clean_topic_part(sensor_name)
    return f"{prefix}/{clean_machine_id}/{clean_sensor_name}"


def build_sensor_message(
    row: dict[str, Any],
    sensor_name: str,
    unit: str,
) -> SensorMessage:
    """Build a SensorMessage from a dataframe row dictionary."""
    required = ["timestamp", "machine_id", sensor_name, "operating_mode", "machine_state", "fault_label"]
    missing = [column for column in required if column not in row]
    if missing:
        raise ValueError("Missing required row fields: " + ", ".join(missing))

    anomaly_score = row.get("anomaly_score")
    health_score = row.get("health_score")

    return SensorMessage(
        timestamp=str(row["timestamp"]),
        machine_id=str(row["machine_id"]),
        sensor_name=sensor_name,
        value=_normalize_value(row[sensor_name]),
        unit=unit,
        operating_mode=str(row["operating_mode"]),
        machine_state=str(row["machine_state"]),
        fault_label=str(row["fault_label"]),
        anomaly_score=float(anomaly_score) if anomaly_score is not None else None,
        health_score=int(health_score) if health_score is not None else None,
    )


def _clean_topic_part(value: str) -> str:
    """Normalize one topic path component."""
    cleaned = str(value).strip().replace(" ", "_")
    if not cleaned:
        raise ValueError("MQTT topic component must not be empty.")
    if "/" in cleaned:
        raise ValueError(f"MQTT topic component must not contain '/': {value!r}")
    return cleaned


def _normalize_value(value: Any) -> float | str | int | bool:
    """Convert common pandas/numpy scalar values into JSON-safe values."""
    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, bool | int | float | str):
        return value

    return str(value)
