# FastAPI Backend

TwinAgent AI includes a FastAPI backend that exposes machine state, incidents, sensor windows, and copilot answers.

---

## Run prerequisites

Before launching the API locally, generate data and export it to SQLite:

```cmd
python scripts\generate_synthetic_data.py
python scripts\run_anomaly_detection.py
python scripts\export_to_sqlite.py
```

Or run the all-in-one bootstrap:

```cmd
python scripts\bootstrap_demo_data.py
```

---

## Launch API

```cmd
python scripts\launch_api.py
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Endpoints

### Health

```text
GET /health
```

Returns:

- project name
- version
- database availability
- sensor row count
- incident count

---

### Latest machine state

```text
GET /machines/latest?machine_id=line1_motor1
```

Returns:

- machine ID
- timestamp
- machine state
- health score
- risk level
- anomaly score
- maintenance urgency
- maintenance recommendation

---

### Machine time window

```text
GET /machines/{machine_id}/window?start_time=...&end_time=...&limit=...
```

Example:

```text
GET /machines/line1_motor1/window?start_time=2026-05-20T14:37:22&end_time=2026-05-20T14:37:30&limit=5
```

Returns sensor rows from SQLite.

---

### List incidents

```text
GET /incidents
```

Optional filter:

```text
GET /incidents?machine_id=line1_motor1
```

---

### Incident detail

```text
GET /incidents/INC-0001
```

Returns:

- incident ID
- machine ID
- time window
- severity
- suspected fault
- anomaly scores
- contributing sensors
- detector evidence

---

### Agent incident question

```text
POST /agent/incident-question
```

Example body:

```json
{
  "incident_id": "INC-0001",
  "question": "Why did this incident trigger and what should the technician inspect first?"
}
```

Returns a deterministic, evidence-grounded copilot answer.

---

## Docker usage

With Docker Compose running:

```cmd
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Current limitations

The API is a demo backend. It does not yet include:

- authentication
- user accounts
- role-based access control
- external database service
- API rate limiting
- production deployment settings
