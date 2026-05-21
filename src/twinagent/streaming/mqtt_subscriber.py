"""MQTT subscriber skeleton for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from twinagent.streaming.message_schema import SensorMessage


MessageHandler = Callable[[str, SensorMessage], None]


@dataclass
class MQTTSensorSubscriber:
    """Subscribe to TwinAgent AI sensor topics.

    This class is intentionally minimal for the MVP. It provides a clean wrapper
    for later ingestion into SQLite or a time-series database.
    """

    broker_host: str = "localhost"
    broker_port: int = 1883
    topic_filter: str = "factory/line1/#"
    received_messages: list[tuple[str, SensorMessage]] = field(default_factory=list)

    def start(self, handler: MessageHandler | None = None) -> None:
        """Start a blocking MQTT subscription loop."""
        try:
            import paho.mqtt.client as mqtt
        except ImportError as error:
            raise ImportError(
                "paho-mqtt is required for live MQTT subscription. "
                "Install it with: pip install -r requirements.txt"
            ) from error

        def on_message(client, userdata, message):  # noqa: ANN001
            payload = message.payload.decode("utf-8")
            sensor_message = SensorMessage.from_json(payload)
            self.received_messages.append((message.topic, sensor_message))

            if handler is not None:
                handler(message.topic, sensor_message)

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_message = on_message
        client.connect(self.broker_host, self.broker_port)
        client.subscribe(self.topic_filter)

        print(
            f"Subscribed to {self.topic_filter} on "
            f"{self.broker_host}:{self.broker_port}. Press Ctrl+C to stop."
        )

        client.loop_forever()
