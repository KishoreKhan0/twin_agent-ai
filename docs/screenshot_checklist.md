# Screenshot Checklist for GitHub README

Use these screenshots for the final README.

## Required screenshots

### 1. Streamlit overview

Open:

```text
http://localhost:8501
```

Capture:

```text
Overview tab with local/fleet summary cards
```

### 2. Sensor intelligence

Capture:

```text
Sensor Intelligence tab with time-series charts
```

### 3. Incidents

Capture:

```text
Incidents tab showing local and fleet incidents
```

### 4. Work orders

Capture:

```text
Work Orders tab showing local/fleet work-order queues
```

### 5. Copilot

Capture:

```text
Copilot tab with a useful answer
```

Example question:

```text
Which machine should maintenance inspect first?
```

### 6. Swagger API

Open:

```text
http://localhost:8000/docs
```

Capture:

```text
Endpoint list showing /health, /summary, /ml/metrics, /work-orders/local, /fleet/summary
```

### 7. Pipeline terminal

Capture terminal output after:

```cmd
python scripts\run_full_pipeline.py
```

Make sure it shows:

```text
Status: passed
Local incidents: 24
Fleet machines: 12
Fleet incidents: 80
ML weighted F1: 0.9332
```

### 8. Docker terminal

Capture terminal after:

```cmd
docker compose up
```

Show both:

```text
twinagent-api
twinagent-dashboard
```

## Recommended README image folder

```text
docs/assets/
```

Suggested names:

```text
docs/assets/overview.png
docs/assets/sensor-intelligence.png
docs/assets/incidents.png
docs/assets/work-orders.png
docs/assets/copilot.png
docs/assets/swagger.png
docs/assets/pipeline-output.png
docs/assets/docker-running.png
```
