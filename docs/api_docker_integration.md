# API and Docker Integration

Step 34 turns the tested backend pipeline into a served artifact API and Docker workflow.

## Normal local workflow

Run the backend pipeline:

```cmd
python scripts\run_full_pipeline.py
```

Start the API:

```cmd
python scripts\launch_api.py
```

Open Swagger:

```text
http://localhost:8000/docs
```

Start the dashboard:

```cmd
python scripts\launch_dashboard.py
```

Open dashboard:

```text
http://localhost:8501
```

## Docker workflow

Build and start API + dashboard:

```cmd
docker compose up --build
```

Open:

```text
API: http://localhost:8000/docs
Dashboard: http://localhost:8501
```

Run the pipeline inside Docker:

```cmd
docker compose --profile pipeline run --rm pipeline
```

## Important note about tests vs pipeline

Tests are not runtime scripts.

Normal usage:

```cmd
python scripts\run_full_pipeline.py
```

Development / before GitHub push:

```cmd
python -m pytest
```

Full validation:

```cmd
python scripts\run_full_pipeline.py --include-tests
```

## New API endpoints

```text
GET  /
GET  /health
GET  /artifacts/status
GET  /summary
GET  /pipeline/summary
POST /pipeline/run
GET  /machine/status
GET  /incidents
GET  /incidents/local
GET  /incidents/reconciled
GET  /incidents/{incident_id}
GET  /ml/metrics
GET  /ml/error-analysis
GET  /ml/feature-importance
GET  /ml/model-card
GET  /work-orders/local
GET  /work-orders/fleet
GET  /fleet/summary
GET  /fleet/incidents
GET  /fleet/triage
GET  /fleet/analysis
```
