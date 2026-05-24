# GitHub Release Checklist

Use this before pushing TwinAgent AI to GitHub.

## 1. Clean validation

Run:

```cmd
python -m pytest
python scripts\run_full_pipeline.py
python scripts\launch_api.py
```

In another terminal:

```cmd
python scripts\smoke_test_api.py
```

Expected:

```text
114 passed
Status: passed
TwinAgent AI API smoke test passed.
```

## 2. Docker validation

```cmd
docker compose up
```

Open:

```text
http://localhost:8000/docs
http://localhost:8501
```

## 3. Screenshot checklist

Create:

```text
docs/assets/
```

Add:

```text
overview.png
sensor-intelligence.png
incidents.png
work-orders.png
copilot.png
swagger.png
pipeline-output.png
docker-running.png
```

## 4. Check repo hygiene

Make sure these are not committed unless you intentionally want them:

```text
.venv/
__pycache__/
.pytest_cache/
data/generated/
data/processed/
data/incidents/
data/reports/
data/fleet/generated/
data/fleet/processed/
data/fleet/incidents/
data/fleet/reports/
models/*.joblib
```

## 5. Git commands

```cmd
git status
git add .
git status
git commit -m "Build TwinAgent AI industrial digital twin pipeline"
git branch -M main
git remote add origin https://github.com/<your-username>/twinagent-ai.git
git push -u origin main
```

If remote already exists:

```cmd
git remote -v
git push -u origin main
```

## 6. Suggested repository topics

```text
industrial-ai
digital-twin
predictive-maintenance
fault-diagnosis
fastapi
streamlit
docker
machine-learning
anomaly-detection
python
```

## 7. Suggested GitHub description

```text
Agentic AI copilot for industrial digital twins: anomaly detection, ML fault diagnosis, fleet triage, work orders, FastAPI, Streamlit, and Docker.
```
