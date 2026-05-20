# TwinAgent AI: Agentic Copilot for Industrial Digital Twins

TwinAgent AI is an agentic AI copilot prototype that monitors a simulated industrial conveyor-motor digital twin, detects sensor anomalies, retrieves engineering knowledge, and generates evidence-grounded maintenance explanations.

## Project status

Current stage: Step 2 — Repository skeleton and environment setup.

This repository will be built step by step. The first working target is a clean Python package that can be installed, imported, and tested locally on Windows.

## Why this project matters

Modern industrial systems generate large volumes of sensor data, but engineers still need reliable tools to understand failures, inspect evidence, and decide what action to take. TwinAgent AI demonstrates how digital twins, anomaly detection, retrieval-augmented generation, and tool-using AI agents can work together in an engineering workflow.

## Planned MVP features

- Synthetic conveyor-motor digital twin
- Configurable sensor simulation
- Fault injection for realistic failure scenarios
- Anomaly detection and incident generation
- Predictive-maintenance health scoring
- Engineering knowledge-base retrieval
- Agentic copilot with tool-calling
- Evidence-grounded explanations with citations
- Streamlit dashboard
- Evaluation using known injected faults

## Technical honesty

This is a prototype built with synthetic data. It does not claim real-world certified predictive-maintenance accuracy or production safety certification.

## Tech stack

Initial MVP stack:

- Python
- NumPy
- Pandas
- PyYAML
- Pydantic
- scikit-learn
- Streamlit
- Plotly
- pytest

Advanced extensions will later include MQTT, FastAPI, Docker, and a visual digital-twin viewer.

## Local setup on Windows CMD

Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the test suite:

```cmd
python -m pytest
```

Expected result at this stage:

```text
1 passed
```

## Current project structure

```text
twinagent-ai/
  README.md
  requirements.txt
  pyproject.toml
  .gitignore

  src/
    twinagent/
      __init__.py

  tests/
    test_package_import.py
```

## Next step

After this setup works, the next implementation step is:

Step 3 — Machine config and synthetic conveyor-motor data generator.
