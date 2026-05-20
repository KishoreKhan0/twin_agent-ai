# Architecture

TwinAgent AI is structured as a local, reproducible industrial-AI prototype. The MVP focuses on a synthetic conveyor-motor digital twin, anomaly detection, incident generation, retrieval over engineering documents, a tool-based copilot, dashboarding, and evaluation.

---

## High-level pipeline

```text
Synthetic conveyor-motor digital twin
        ↓
Generated time-series CSV
        ↓
Anomaly detection
        ↓
Incident generation
        ↓
Health scoring and maintenance recommendation
        ↓
Engineering document retrieval
        ↓
Agentic copilot explanation
        ↓
Dashboard / report / evaluation
```

---

## Design goals

The architecture is designed to be:

- modular
- testable
- Windows-friendly
- easy to run locally
- honest about synthetic data
- extensible toward MQTT, APIs, Docker, and real databases

---

## Main modules

### `simulation/`

Responsible for generating synthetic industrial machine data.

Key files:

```text
machine_simulator.py
sensor_models.py
fault_profiles.py
```

Responsibilities:

- generate normal operating patterns
- inject faults
- add realistic noise
- produce timestamped sensor data
- write CSV outputs

---

### `analytics/`

Responsible for anomaly detection, incident creation, health scoring, and maintenance recommendations.

Key files:

```text
anomaly_detection.py
incident_detector.py
health_score.py
predictive_maintenance.py
```

Responsibilities:

- score sensor anomalies
- convert anomaly rows to incident windows
- calculate health score
- assign risk level
- produce maintenance urgency and recommendation

---

### `rag/`

Responsible for local engineering-document retrieval.

Key files:

```text
document_loader.py
chunking.py
vector_store.py
retriever.py
```

Responsibilities:

- load Markdown knowledge-base files
- split documents into chunks
- retrieve relevant chunks with a local TF-IDF representation
- return citation-friendly source metadata

The MVP intentionally uses local retrieval to avoid external model downloads.

---

### `agent/`

Responsible for the tool-based copilot and incident report generation.

Key files:

```text
tools.py
agent_orchestrator.py
report_writer.py
prompts.py
```

Responsibilities:

- load incidents
- query sensor windows
- summarize evidence
- retrieve engineering references
- generate maintenance checklist
- produce grounded copilot answers
- export Markdown incident reports

---

### `dashboard/`

Responsible for the Streamlit UI.

Key files:

```text
streamlit_app.py
components.py
charts.py
```

Responsibilities:

- load processed outputs
- show machine overview
- visualize sensor timelines
- visualize anomaly and health trends
- display incidents
- run copilot explanations

---

### `evaluation/`

Responsible for benchmark metrics.

Key files:

```text
metrics.py
benchmark.py
```

Responsibilities:

- compute binary detection metrics
- compute detection delay
- compute incident overlap
- compute row-level suspected-fault alignment
- compute incident-level diagnosis accuracy
- export JSON and Markdown reports

---

## Current storage model

The MVP uses local files:

```text
data/generated/sensor_data.csv
data/processed/sensor_data_with_anomalies.csv
data/incidents/incidents.json
data/reports/evaluation_metrics.json
data/reports/evaluation_report.md
data/reports/INC-0001_report.md
```

This is intentionally simple. SQLite, MQTT, and Docker will be added after the local MVP remains stable.

---

## Why deterministic tools first?

The project uses a deterministic tool-based agent before adding an LLM because:

- the core engineering workflow becomes testable
- outputs are reproducible
- no API key is needed
- hallucination risk is reduced
- the future LLM layer can call the same tools

---

## Future architecture extensions

Planned extensions:

```text
Simulator → MQTT publisher → Mosquitto → ingestion service
                                          ↓
                                      SQLite / time-series DB
                                          ↓
                                   FastAPI backend
                                          ↓
                             Dashboard / agent / report tools
```

A later Docker Compose setup can include:

- dashboard service
- backend service
- Mosquitto broker
- database service
