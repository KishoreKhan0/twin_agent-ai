"""MQTT publisher utilities for TwinAgent AI sensor replay."""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Iterable

import pandas as pd

from twinagent.streaming.message_schema import SensorMessage, build_sensor_message, topic_for_sensor


DEFAULT_SENSOR_UNITS = {
    "temperature_c": "degC",
    "vibration_mm_s": "mm/s",
    "rpm": "rpm",
    "current_a": "A",
    "load_pct": "%",
    "belt_speed_mps": "m/s",
    "throughput_units_min": "units/min",
    "ambient_temperature_c": "degC",
}


@dataclass
class MQTTSensorPublisher:
    """Replay sensor rows as MQTT messages.

    Dry-run mode does not require a broker or paho-mqtt. It returns the messages
    that would have been published, making the streaming layer testable locally.
    """

    broker_host: str = "localhost"
    broker_port: int = 1883
    topic_prefix: str = "factory/line1"
    sensor_units: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_SENSOR_UNITS))

    def replay_dataframe(
        self,
        dataframe: pd.DataFrame,
        sensor_names: Iterable[str] | None = None,
        delay_seconds: float = 0.0,
        dry_run: bool = True,
        limit_rows: int | None = None,
    ) -> list[tuple[str, SensorMessage]]:
        """Replay dataframe rows as MQTT messages or dry-run messages."""
        if dataframe.empty:
            raise ValueError("Cannot replay an empty dataframe.")

        selected_sensors = list(sensor_names or self.sensor_units.keys())
        missing = [sensor for sensor in selected_sensors if sensor not in dataframe.columns]
        if missing:
            raise ValueError("Missing sensor columns: " + ", ".join(missing))

        rows = dataframe.head(limit_rows) if limit_rows is not None else dataframe
        messages: list[tuple[str, SensorMessage]] = []

        mqtt_client = None
        if not dry_run:
            mqtt_client = self._create_connected_client()

        try:
            for _, row in rows.iterrows():
                row_dict = row.to_dict()
                for sensor_name in selected_sensors:
                    message = build_sensor_message(
                        row=row_dict,
                        sensor_name=sensor_name,
                        unit=self.sensor_units.get(sensor_name, ""),
                    )
                    topic = topic_for_sensor(
                        message.machine_id,
                        sensor_name,
                        prefix=self.topic_prefix,
                    )

                    if mqtt_client is not None:
                        mqtt_client.publish(topic, message.to_json())

                    messages.append((topic, message))

                if delay_seconds > 0:
                    time.sleep(delay_seconds)
        finally:
            if mqtt_client is not None:
                mqtt_client.disconnect()

        return messages

    def _create_connected_client(self):
        """Create and connect a paho-mqtt client lazily."""
        try:
            import paho.mqtt.client as mqtt
        except ImportError as error:
            raise ImportError(
                "paho-mqtt is required for live MQTT publishing. "
                "Install it with: pip install -r requirements.txt"
            ) from error

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect(self.broker_host, self.broker_port)
        client.loop_start()
        return client
