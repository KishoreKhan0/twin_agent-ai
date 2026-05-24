# TwinAgent AI: Agentic Copilot for Industrial Digital Twins


---

**TwinAgent AI is an agentic AI copilot prototype that monitors a simulated industrial conveyor-motor digital twin, detects sensor anomalies, retrieves engineering knowledge, and generates evidence-grounded maintenance explanations through a dashboard and API.**

---

## System architecture

```text
Synthetic conveyor-motor digital twin
        ↓
Generated sensor CSV
        ↓
Anomaly detection
        ↓
Incident generation
        ↓
Health score + maintenance urgency
        ↓
SQLite persistence
        ↓
Engineering knowledge retrieval
        ↓
Tool-based agentic copilot
        ↓
FastAPI backend + Streamlit dashboard
        ↓
Markdown report export + evaluation metrics
        ↓
Docker Compose demo
```

---
## License

MIT License. See `LICENSE`.
## Implemented features

### Digital twin simulation

- Configurable synthetic conveyor-motor simulator
- Normal operating behavior with load variation and sensor noise
- Fault injection for bearing wear, overheating, belt misalignment, motor overload, sensor drift, and cooling failure
- Deterministic data generation using a random seed

### Analytics

- Interpretable anomaly scoring
- Incident grouping
- Health-score calculation
- Risk-level classification
- Maintenance urgency assignment
- Maintenance recommendation generation

### RAG and agentic copilot

- Local Markdown engineering knowledge base
- Local TF-IDF retrieval
- Citation-friendly retrieved references
- Tool-based copilot that queries incidents, sensor windows, retrieved documents, and maintenance checklist logic
- Evidence-grounded answers with uncertainty statements

### Dashboard

- Streamlit UI
- Machine overview
- Sensor timelines
- Anomaly score timeline
- Health score timeline
- Incident table
- Incident details
- Copilot explanation panel

### API

- FastAPI backend
- Swagger UI at `/docs`
- Health endpoint
- Machine latest-state endpoint
- Machine time-window endpoint
- Incident list/detail endpoints
- Agent question endpoint

### Storage and streaming

- SQLite storage layer for processed sensor rows and incidents
- MQTT-style dry-run sensor replay
- Optional live MQTT publisher/subscriber skeleton with `paho-mqtt`

### Evaluation and reporting

- Binary anomaly detection metrics
- Detection delay
- Incident overlap score
- Incident-level diagnosis accuracy
- Row-level fault alignment metric
- JSON and Markdown evaluation reports
- Markdown incident report export

### Docker

- Dockerfile
- Docker Compose setup
- API container
- Dashboard container
- Demo-data bootstrap script

---

## Current evaluation snapshot

Default evaluation output:

```text
Precision: 1.0
Recall: 0.7076
F1 score: 0.8287
False positive rate: 0.0
Mean detection delay seconds: 142.0
Incident overlap score: 0.8924
Incident diagnosis accuracy: 1.0
Row-level fault alignment accuracy: 0.1852
```

Interpretation:

- Binary detection is strong for the current synthetic fault setup.
- Incident-level diagnosis is the most relevant diagnosis metric because the copilot explains incidents.
- Row-level fault alignment is stricter and lower because fault windows can overlap and evolve.
- Results are measured on synthetic data and should not be presented as real-world predictive-maintenance accuracy.

---

## Tech stack

- Python
- NumPy
- Pandas
- PyYAML
- Pydantic
- scikit-learn
- Plotly
- Streamlit
- FastAPI
- Uvicorn
- SQLite
- paho-mqtt
- pytest
- Docker / Docker Compose

---

## Local setup on Windows CMD

Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run tests:

```cmd
python -m pytest
```

Expected current result:

```text
57 passed
```

---

## Local demo commands

Run the core pipeline:

```cmd
python scripts\generate_synthetic_data.py
python scripts\run_anomaly_detection.py
python scripts\export_to_sqlite.py
python scripts\run_agent.py
python scripts\evaluate_detectors.py
python scripts\export_incident_report.py --incident-id INC-0001
```

Launch the Streamlit dashboard:

```cmd
python scripts\launch_dashboard.py
```

Open:

```text
http://localhost:8501
```

Launch the FastAPI backend:

```cmd
python scripts\launch_api.py
```

Open:

```text
http://127.0.0.1:8000/docs
```

Run MQTT-style dry-run replay:

```cmd
python scripts\replay_sensor_stream.py --dry-run --limit-rows 2
```

Bootstrap all demo artifacts in one command:

```cmd
python scripts\bootstrap_demo_data.py
```

---

## Docker demo

Build and run both API and dashboard:

```cmd
docker compose up --build
```

Open:

```text
FastAPI Swagger UI: http://127.0.0.1:8000/docs
Streamlit dashboard: http://127.0.0.1:8501
```

Run tests inside Docker:

```cmd
docker compose run --rm api python -m pytest
```

Stop containers:

```cmd
docker compose down
```

---

## Generated outputs

The pipeline creates:

```text
data/generated/sensor_data.csv
data/processed/sensor_data_with_anomalies.csv
data/processed/twinagent.db
data/incidents/incidents.json
data/reports/evaluation_metrics.json
data/reports/evaluation_report.md
data/reports/INC-0001_report.md
```

---

## API endpoints

```text
GET  /health
GET  /machines/latest?machine_id=line1_motor1
GET  /machines/{machine_id}/window
GET  /incidents
GET  /incidents/{incident_id}
POST /agent/incident-question
```

Example POST body:

```json
{
  "incident_id": "INC-0001",
  "question": "Why did this incident trigger and what should the technician inspect first?"
}
```

---

## Documentation

See:

- `docs/architecture.md`
- `docs/simulation.md`
- `docs/anomaly_detection.md`
- `docs/rag_agent.md`
- `docs/dashboard.md`
- `docs/evaluation.md`
- `docs/storage.md`
- `docs/mqtt_streaming.md`
- `docs/api.md`
- `docs/docker.md`
- `docs/completion_checklist.md`
- `docs/cv_notes.md`

---

## Technical honesty and limitations

This is a prototype built with synthetic data.

It does **not** claim:

- certified safety behavior
- real-world predictive-maintenance accuracy
- production deployment readiness
- confirmed physical fault diagnosis
- validated remaining-useful-life estimation

Correct wording:

- synthetic industrial digital twin
- simulated sensor stream
- anomaly-detection prototype
- predictive-maintenance scoring proxy
- evidence-grounded incident explanation
- agentic AI copilot prototype

---
