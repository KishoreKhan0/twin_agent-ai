# Project Completion Checklist

This checklist verifies the current TwinAgent AI MVP.

---

## 1. Local tests

Run:

```cmd
python -m pytest
```

Expected:

```text
57 passed
```

---

## 2. Data generation

Run:

```cmd
python scripts\generate_synthetic_data.py
```

Expected output:

```text
Rows generated: 3600
Saved CSV: data\generated\sensor_data.csv
```

---

## 3. Anomaly detection

Run:

```cmd
python scripts\run_anomaly_detection.py
```

Expected output includes:

```text
Anomaly rows: 934
Incidents created: 1
INC-0001 | high | bearing_wear
```

---

## 4. SQLite export

Run:

```cmd
python scripts\export_to_sqlite.py
```

Expected output includes:

```text
Sensor rows written: 3600
Incidents written: 1
```

---

## 5. Copilot answer

Run:

```cmd
python scripts\run_agent.py
```

Expected answer sections:

```text
Incident summary
Sensor evidence
Engineering document guidance
Recommended maintenance actions
Uncertainty and limits
```

---

## 6. Evaluation

Run:

```cmd
python scripts\evaluate_detectors.py
```

Expected metrics include:

```text
Precision: 1.0
Recall: 0.7076
F1 score: 0.8287
Incident overlap score: 0.8924
Incident diagnosis accuracy: 1.0
```

---

## 7. Incident report export

Run:

```cmd
python scripts\export_incident_report.py --incident-id INC-0001
```

Expected output:

```text
data\reports\INC-0001_report.md
```

---

## 8. MQTT dry-run streaming

Run:

```cmd
python scripts\replay_sensor_stream.py --dry-run --limit-rows 2
```

Expected output:

```text
Messages generated: 16
```

---

## 9. FastAPI backend

Run:

```cmd
python scripts\launch_api.py
```

Open:

```text
http://127.0.0.1:8000/docs
```

Expected endpoints:

```text
/health
/machines/latest
/machines/{machine_id}/window
/incidents
/incidents/{incident_id}
/agent/incident-question
```

---

## 10. Streamlit dashboard

Run:

```cmd
python scripts\launch_dashboard.py
```

Open:

```text
http://localhost:8501
```

Expected sections:

```text
Machine overview
Sensor and health timelines
Incidents
AI copilot explanation
```

---

## 11. Docker Compose

Run:

```cmd
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8501
```

Run Docker tests:

```cmd
docker compose run --rm api python -m pytest
```

Expected:

```text
57 passed
```

---

## MVP completion status

The MVP is complete when all items above pass.

Current completed modules:

- simulation
- anomaly detection
- incident generation
- health scoring
- maintenance recommendation
- RAG retrieval
- deterministic copilot
- dashboard
- evaluation
- Markdown report export
- SQLite storage
- MQTT dry-run streaming
- FastAPI backend
- Docker Compose demo
- GitHub documentation

---

## Suggested final polish before GitHub upload

Optional but recommended:

- add screenshots to `assets/images/`
- update GitHub repository URL in README if needed
- add a short demo GIF
- check that generated data files are not accidentally committed if `.gitignore` excludes them
- commit source code, configs, tests, docs, and knowledge base
- do not commit `.venv/`, caches, or temporary files
