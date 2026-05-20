# TwinAgent AI: Agentic Copilot for Industrial Digital Twins

TwinAgent AI is an agentic AI copilot prototype that monitors a simulated industrial conveyor-motor digital twin, detects sensor anomalies, retrieves engineering knowledge, and generates evidence-grounded maintenance explanations.

> **Status:** MVP core implemented: simulation, anomaly detection, health scoring, RAG retrieval, deterministic agentic copilot, Streamlit dashboard, evaluation, and Markdown incident reports.

---

## Why this project matters

Modern industrial systems generate large volumes of sensor data, but engineers still need reliable tools to understand failures, inspect evidence, retrieve relevant documentation, and decide what action to take.

TwinAgent AI demonstrates how the following can work together in an engineering workflow:

- synthetic industrial digital twins
- time-series sensor analytics
- anomaly detection
- predictive-maintenance scoring
- retrieval-augmented engineering knowledge
- agentic tool-calling workflows
- dashboard visualization
- evaluation against known fault labels

The project is intentionally built as an engineering prototype rather than a toy chatbot.

---

## One-sentence pitch

**TwinAgent AI is an agentic AI copilot prototype that monitors a simulated industrial conveyor-motor digital twin, detects sensor anomalies, retrieves engineering knowledge, and generates evidence-grounded maintenance explanations through a dashboard.**

---

## Core scenario

The MVP simulates:

```text
Factory Line 1 — Conveyor Motor 1
machine_id = line1_motor1
```

The simulated system represents an electric conveyor motor with a belt, bearing assembly, load variation, cooling behavior, and multiple sensor channels.

### Simulated sensors

```text
temperature_c
vibration_mm_s
rpm
current_a
load_pct
belt_speed_mps
throughput_units_min
ambient_temperature_c
machine_state
fault_label
fault_severity
```

### Fault types

The simulator currently supports:

- bearing wear
- overheating
- belt misalignment
- motor overload
- sensor drift
- cooling failure

The default demo injects a bearing-wear event followed by overlapping overheating and belt-misalignment behavior.

---

## System architecture

```text
Synthetic conveyor-motor digital twin
        ↓
CSV time-series dataset
        ↓
Anomaly detection
        ↓
Incident generation
        ↓
Health score + maintenance urgency
        ↓
Engineering knowledge-base retrieval
        ↓
Tool-based agentic copilot
        ↓
Streamlit dashboard + Markdown incident report
        ↓
Evaluation against known simulated fault labels
```

For the MVP, the project deliberately uses local files and deterministic tools to keep the system reproducible on Windows.

---

## Implemented MVP features

- Configurable synthetic conveyor-motor simulator
- Fault injection with realistic sensor effects
- CSV-based time-series data generation
- Interpretable anomaly detection
- Incident grouping
- Health-score calculation
- Rule-based predictive-maintenance recommendations
- Synthetic engineering knowledge base
- Local TF-IDF retrieval with source references
- Deterministic tool-based agentic copilot
- Streamlit dashboard
- Evaluation metrics and benchmark reports
- Markdown incident report export
- Pytest test suite

---

## Current evaluation snapshot

The current default run produces:

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
- Incident-level diagnosis is the main diagnosis metric for this MVP because the copilot explains incidents.
- Row-level fault alignment is stricter and lower because fault labels can overlap and evolve over time.
- These metrics are measured on synthetic data and should not be presented as real-world predictive-maintenance accuracy.

---

## Example incident

The default generated incident is:

```text
INC-0001
Machine: line1_motor1
Severity: high
Suspected fault: bearing_wear
Time window: 2026-05-20T14:37:22 → 2026-05-20T14:56:59
```

The copilot explains the incident using:

- sensor evidence
- detector evidence
- retrieved engineering references
- maintenance actions
- uncertainty statements

---

## Tech stack

### Current MVP

- Python
- NumPy
- Pandas
- PyYAML
- scikit-learn
- Plotly
- Streamlit
- pytest
- local TF-IDF retrieval

### Planned extensions

- MQTT + Mosquitto
- FastAPI
- Docker / Docker Compose
- SQLite or time-series database integration
- optional LLM-backed agent layer
- optional 3D digital-twin visualization

---

## Repository structure

```text
twinagent-ai/
  README.md
  requirements.txt
  pyproject.toml
  .gitignore

  configs/
    machine_config.yaml
    anomaly_config.yaml
    rag_config.yaml

  data/
    generated/
    processed/
    incidents/
    reports/

  docs/
    architecture.md
    simulation.md
    anomaly_detection.md
    rag_agent.md
    dashboard.md
    evaluation.md
    cv_notes.md

  knowledge_base/
    motor_manual.md
    conveyor_maintenance_guide.md
    fault_code_reference.md
    safety_checklist.md
    bearing_failure_notes.md
    sensor_specs.md
    maintenance_log_q1.md

  scripts/
    generate_synthetic_data.py
    run_anomaly_detection.py
    run_agent.py
    launch_dashboard.py
    evaluate_detectors.py
    export_incident_report.py

  src/
    twinagent/
      simulation/
      analytics/
      rag/
      agent/
      dashboard/
      evaluation/

  tests/
```

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
41 passed
```

---

## Quickstart demo

Run the full MVP pipeline:

```cmd
python scripts\generate_synthetic_data.py
python scripts\run_anomaly_detection.py
python scripts\run_agent.py
python scripts\evaluate_detectors.py
python scripts\export_incident_report.py --incident-id INC-0001
```

Launch the dashboard:

```cmd
python scripts\launch_dashboard.py
```

Or directly:

```cmd
streamlit run src\twinagent\dashboard\streamlit_app.py
```

Then open the local Streamlit URL printed in the terminal.

---

## Generated outputs

After running the pipeline, the project creates:

```text
data/generated/sensor_data.csv
data/processed/sensor_data_with_anomalies.csv
data/incidents/incidents.json
data/reports/evaluation_metrics.json
data/reports/evaluation_report.md
data/reports/INC-0001_report.md
```

---

## Dashboard

The Streamlit dashboard includes:

- machine overview
- current health score
- risk level
- anomaly count
- sensor timelines
- anomaly score timeline
- health score timeline
- incident table
- selected incident details
- copilot explanation panel

Suggested screenshot locations for GitHub:

```text
assets/images/dashboard_overview.png
assets/images/incident_detail.png
assets/images/copilot_answer.png
```

---

## Example copilot question

```text
Why did this incident trigger and what should the technician inspect first?
```

The copilot answer includes:

- incident summary
- sensor evidence
- retrieved engineering references
- recommended technician actions
- uncertainty and limitations

The system does not claim physical confirmation. It describes the result as a suspected fault based on synthetic sensor evidence and retrieved engineering guidance.

---

## Documentation

See:

- `docs/architecture.md`
- `docs/simulation.md`
- `docs/anomaly_detection.md`
- `docs/rag_agent.md`
- `docs/dashboard.md`
- `docs/evaluation.md`
- `docs/cv_notes.md`

---

## Technical honesty and limitations

This project is a prototype using synthetic data.

It does **not** claim:

- certified safety behavior
- real-world predictive-maintenance accuracy
- production deployment readiness
- confirmed physical failure diagnosis

Correct wording:

- synthetic industrial digital twin
- simulated sensor stream
- anomaly-detection prototype
- predictive-maintenance scoring proxy
- evidence-grounded incident explanation
- agentic AI copilot prototype

---

## Roadmap

Next planned extensions:

1. SQLite persistence layer
2. MQTT live streaming with Mosquitto
3. FastAPI backend
4. Docker Compose demo
5. richer benchmark comparisons
6. optional LLM-backed agent
7. optional 3D conveyor/motor visualization

---

## CV positioning

```latex
\item{
\textbf{TwinAgent AI: Agentic Copilot for Industrial Digital Twins} \hfill \textit{2026} \\
- Built an agentic AI copilot prototype for industrial digital-twin workflows, combining synthetic conveyor-motor sensor simulation, anomaly detection, predictive-maintenance scoring, RAG-style engineering-document retrieval, and evidence-grounded incident explanations.

- Developed a modular Python pipeline with configurable fault injection, incident generation, health scoring, evaluation metrics, Markdown report export, and an interactive Streamlit dashboard for machine health monitoring and failure analysis.

- Evaluated anomaly detection against known simulated fault labels, reporting precision, recall, F1 score, detection delay, incident overlap, and incident-level diagnosis accuracy while clearly documenting synthetic-data limitations.
}
```

---

## License

MIT License.
