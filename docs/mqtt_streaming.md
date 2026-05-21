# MQTT Streaming

TwinAgent AI includes an MQTT-style streaming skeleton for replaying sensor data.

---

## Purpose

The streaming layer prepares the project for live sensor ingestion workflows.

Current MVP supports:

- dry-run message replay
- MQTT topic generation
- JSON sensor-message schema
- optional live MQTT publisher
- optional subscriber skeleton

---

## Dry-run replay

Dry-run mode does not require Mosquitto or any MQTT broker.

Run:

```cmd
python scripts\replay_sensor_stream.py --dry-run --limit-rows 2
```

Expected result:

```text
TwinAgent AI sensor stream replay complete.
Mode: dry-run
Input rows replayed: 2
Messages generated: 16
```

Why 16 messages?

```text
2 rows × 8 sensors = 16 messages
```

---

## Topic format

```text
factory/line1/{machine_id}/{sensor_name}
```

Example:

```text
factory/line1/line1_motor1/temperature_c
```

---

## Message format

Example JSON payload:

```json
{
  "timestamp": "2026-05-20T14:00:00",
  "machine_id": "line1_motor1",
  "sensor_name": "temperature_c",
  "value": 59.59,
  "unit": "degC",
  "operating_mode": "production",
  "machine_state": "normal",
  "fault_label": "normal",
  "anomaly_score": 0.0,
  "health_score": 100
}
```

---

## Live MQTT publishing

Start a broker first, then run:

```cmd
python scripts\replay_sensor_stream.py --live --limit-rows 10
```

The code uses `paho-mqtt`.

---

## Subscriber skeleton

The subscriber class is available in:

```text
src/twinagent/streaming/mqtt_subscriber.py
```

It can subscribe to:

```text
factory/line1/#
```

A future step can connect subscriber messages directly into SQLite or a time-series database.

---

## Current limitations

The current streaming layer is a skeleton. It does not yet include:

- guaranteed delivery
- message buffering
- retained messages
- broker authentication
- schema registry
- ingestion service
- live dashboard updates
