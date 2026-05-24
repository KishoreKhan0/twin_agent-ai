# TwinAgent AI Runbook

## Normal local run

```cmd
python -m pytest
python scripts\run_full_pipeline.py
python scripts\launch_api.py
```

In another terminal:

```cmd
python scripts\launch_dashboard.py
```

Open:

```text
http://localhost:8000/docs
http://localhost:8501
```

## Docker run

First build:

```cmd
docker compose up --build
```

Later starts:

```cmd
docker compose up
```

Stop:

```cmd
docker compose down
```

## API validation

With API running:

```cmd
python scripts\smoke_test_api.py
```

Expected:

```text
TwinAgent AI API smoke test passed.
```

## If API endpoints show missing artifacts

Run:

```cmd
python scripts\run_full_pipeline.py
```

Then restart API/Docker.

## If Docker is slow

First build is slow because dependencies are installed.

After first build, use:

```cmd
docker compose up
```

Rebuild only after changing:

```text
Dockerfile
requirements.txt
Python dependencies
docker-compose.yml build settings
```

## If Swagger shows 422

That usually means required parameters were missing.

Examples:

```text
/machines/{machine_id}/window requires machine_id, start_time, end_time
/incidents/{incident_id} requires incident_id
/agent/incident-question requires JSON body
/ml/feature-importance requires limit between 1 and 500
```

## Useful endpoint test values

Machine window:

```text
machine_id: line1_motor1
start_time: 2026-05-20T14:37:22
end_time: 2026-05-20T14:37:30
limit: 5
```

Incident detail:

```text
incident_id: INC-0001
```

Agent question body:

```json
{
  "incident_id": "INC-0001",
  "question": "Why did this incident trigger?",
  "copilot_mode": "deterministic"
}
```

## Final validation checklist

```cmd
python -m pytest
python scripts\run_full_pipeline.py
python scripts\launch_api.py
python scripts\smoke_test_api.py
docker compose up
```

Check:

```text
http://localhost:8000/docs
http://localhost:8501
```
