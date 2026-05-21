# Docker Demo

TwinAgent AI includes a Docker Compose setup for running the API and dashboard as containers.

---

## Services

```text
api        -> FastAPI backend on http://127.0.0.1:8000
dashboard  -> Streamlit dashboard on http://127.0.0.1:8501
```

Both services use the same project image and bootstrap demo data on startup.

---

## Files

```text
Dockerfile
docker-compose.yml
.dockerignore
scripts/bootstrap_demo_data.py
```

---

## Prerequisites

Install Docker Desktop and make sure it is running.

Check Docker:

```cmd
docker --version
docker compose version
```

---

## Build and run

From the project root:

```cmd
docker compose up --build
```

Open:

```text
FastAPI Swagger UI: http://127.0.0.1:8000/docs
Streamlit dashboard: http://127.0.0.1:8501
```

---

## Stop containers

Press `Ctrl+C`, then run:

```cmd
docker compose down
```

---

## Run tests inside Docker

```cmd
docker compose run --rm api python -m pytest
```

Expected:

```text
57 passed
```

---

## Bootstrap behavior

Each service runs:

```cmd
python scripts/bootstrap_demo_data.py
```

before starting the API or dashboard.

The bootstrap creates:

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

## Current limitations

This Docker setup is demo-oriented. It does not yet include:

- production reverse proxy
- HTTPS
- authentication
- persistent external database volume
- separate MQTT broker service
- monitoring stack
- cloud deployment configuration

It is suitable for local portfolio demonstration and reproducible project review.
