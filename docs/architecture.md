# TwinAgent AI Architecture

## System overview

TwinAgent AI is organized as a pipeline-first industrial AI system.

```text
Sensor simulation
    ↓
Anomaly detection
    ↓
Health scoring
    ↓
Incident detection
    ↓
ML fault diagnosis
    ↓
ML explainability
    ↓
ML incident enrichment
    ↓
Diagnosis reconciliation
    ↓
Work-order generation
    ↓
FastAPI + Streamlit + Docker
```

## Core components

### Simulation

Generates deterministic synthetic conveyor-motor sensor data with labeled fault windows.

Key outputs:

```text
data/generated/sensor_data.csv
data/fleet/generated/fleet_sensor_data.csv
```

### Anomaly detection

Detects abnormal patterns in temperature, vibration, current, RPM, load, throughput, and related machine signals.

Key output:

```text
data/processed/sensor_data_with_anomalies.csv
```

### ML fault diagnosis

Builds time-windowed features and trains a Random Forest classifier.

Key outputs:

```text
models/fault_classifier.joblib
models/fault_classifier_metrics.json
data/processed/sensor_data_with_fault_predictions.csv
```

### Diagnosis reconciliation

Combines rule diagnosis and ML diagnosis into one final technician-facing decision.

Key output:

```text
data/incidents/incidents_reconciled.json
```

### Work orders

Turns incidents into technician-ready maintenance actions.

Key outputs:

```text
data/reports/local_work_orders.json
data/fleet/reports/fleet_work_orders.json
```

### API

Serves generated artifacts through FastAPI.

Entry point:

```text
src/twinagent/api/app.py
```

### Dashboard

Provides operational monitoring and copilot access through Streamlit.

Entry point:

```text
src/twinagent/dashboard/streamlit_app.py
```

### Pipeline orchestrator

Runs the complete backend workflow.

Entry point:

```text
scripts/run_full_pipeline.py
```

## Deployment architecture

Docker Compose starts:

```text
api        → FastAPI on port 8000
dashboard  → Streamlit on port 8501
```

Optional profile:

```text
pipeline   → one-shot full pipeline run
```

## Design principle

The API and dashboard are artifact-driven. They serve outputs produced by the tested backend pipeline. This keeps local, Docker, and CI validation consistent.
