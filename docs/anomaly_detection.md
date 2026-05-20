# Anomaly Detection

The anomaly detection module identifies abnormal sensor behavior and groups anomaly rows into incidents.

---

## Input

```text
data/generated/sensor_data.csv
```

---

## Output

```text
data/processed/sensor_data_with_anomalies.csv
data/incidents/incidents.json
```

---

## Detection approach

The MVP uses interpretable threshold-based scoring.

Each configured sensor receives a sensor-specific anomaly score. These scores are combined into one final `anomaly_score`.

Main outputs:

```text
anomaly_score
is_anomaly
anomaly_severity
contributing_sensors
suspected_fault
```

---

## Sensor-specific logic

### Temperature

High values indicate thermal stress.

Example logic:

```text
temperature_c >= warning_min → warning score
temperature_c >= high_min    → high score
```

### Vibration

High vibration is important for bearing and alignment faults.

Example logic:

```text
vibration_mm_s >= warning_min → warning score
vibration_mm_s >= high_min    → high score
```

### Current

High current suggests overload or mechanical resistance.

### RPM

RPM is evaluated as an outside-band sensor because both unusually low and unusually high values can be abnormal.

### Throughput

Throughput is evaluated as a lower-bound sensor because low throughput is abnormal.

---

## Incident grouping

Rows with `is_anomaly = True` are grouped into incidents using:

- minimum duration
- maximum allowed gap between anomaly points

The default run creates:

```text
INC-0001
severity: high
suspected_fault: bearing_wear
time window: 2026-05-20T14:37:22 → 2026-05-20T14:56:59
```

---

## Health scoring

After anomaly detection, the pipeline adds:

```text
health_score
risk_level
maintenance_urgency
maintenance_recommendation
```

The health score is an interpretable proxy based on:

- anomaly score
- anomaly severity
- machine state
- sensor stress

It is not a real remaining-useful-life model.

---

## Maintenance recommendation

The maintenance advisor produces concise rule-based recommendations such as:

- inspect bearing housing
- check lubrication condition
- inspect cooling airflow
- inspect belt alignment
- reduce load if the machine remains critical

---

## Run command

```cmd
python scripts\run_anomaly_detection.py
```

---

## Technical honesty

The detector is an interpretable prototype. It is useful for demonstrating an industrial AI workflow with known synthetic ground truth, but it should not be described as a production-grade predictive-maintenance model.
