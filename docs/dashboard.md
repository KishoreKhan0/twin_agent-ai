# Dashboard

TwinAgent AI includes a Streamlit dashboard for inspecting the digital-twin pipeline visually.

---

## Run command

```cmd
python scripts\launch_dashboard.py
```

Alternative:

```cmd
streamlit run src\twinagent\dashboard\streamlit_app.py
```

---

## Required generated files

Before launching the dashboard, run:

```cmd
python scripts\generate_synthetic_data.py
python scripts\run_anomaly_detection.py
```

The dashboard expects:

```text
data/processed/sensor_data_with_anomalies.csv
data/incidents/incidents.json
```

---

## Dashboard sections

### 1. Machine overview

Shows:

- machine ID
- latest machine state
- latest health score
- latest risk level
- number of incidents
- maximum anomaly score
- minimum health score
- anomaly row count

### 2. Sensor and health timelines

Shows:

- selected sensor timeline
- anomaly score timeline
- machine health score timeline

The user can filter by start and end time.

### 3. Incidents

Shows:

- incident table
- selected incident detail
- severity
- suspected fault
- time window
- contributing sensors
- detector evidence

### 4. AI copilot explanation

Allows the user to select an incident and ask a question.

The copilot response includes:

- incident summary
- sensor evidence
- retrieved engineering references
- recommended maintenance actions
- uncertainty and limits

---

## Suggested screenshots

For GitHub, capture:

```text
assets/images/dashboard_overview.png
assets/images/incident_detail.png
assets/images/copilot_answer.png
```

---

## Current limitation

The dashboard reads generated local files. It does not yet use a FastAPI backend or live MQTT stream. Those are planned extensions after the MVP.
