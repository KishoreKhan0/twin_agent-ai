"""Tests for TwinAgent AI MQTT streaming skeleton."""

from __future__ import annotations

from pathlib import Path

from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation.machine_simulator import MachineSimulator
from twinagent.streaming import MQTTSensorPublisher, SensorMessage, build_sensor_message, topic_for_sensor


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _processed_dataframe():
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    health = HealthScoreCalculator()
    processed = health.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    return advisor.add_maintenance_columns(processed)


def test_topic_for_sensor() -> None:
    topic = topic_for_sensor("line1_motor1", "temperature_c")

    assert topic == "factory/line1/line1_motor1/temperature_c"


def test_sensor_message_round_trip_json() -> None:
    message = SensorMessage(
        timestamp="2026-05-20T14:00:00",
        machine_id="line1_motor1",
        sensor_name="temperature_c",
        value=52.4,
        unit="degC",
        operating_mode="production",
        machine_state="normal",
        fault_label="normal",
        anomaly_score=0.0,
        health_score=100,
    )

    restored = SensorMessage.from_json(message.to_json())

    assert restored == message


def test_build_sensor_message_from_row() -> None:
    dataframe = _processed_dataframe()
    row = dataframe.iloc[0].to_dict()

    message = build_sensor_message(row, sensor_name="temperature_c", unit="degC")

    assert message.machine_id == "line1_motor1"
    assert message.sensor_name == "temperature_c"
    assert message.unit == "degC"
    assert message.timestamp == "2026-05-20T14:00:00"


def test_mqtt_publisher_dry_run_generates_messages() -> None:
    dataframe = _processed_dataframe()
    publisher = MQTTSensorPublisher()

    messages = publisher.replay_dataframe(
        dataframe,
        sensor_names=["temperature_c", "vibration_mm_s"],
        dry_run=True,
        limit_rows=3,
    )

    assert len(messages) == 6
    assert messages[0][0].endswith("/temperature_c")
    assert messages[1][0].endswith("/vibration_mm_s")
    assert messages[0][1].machine_id == "line1_motor1"
