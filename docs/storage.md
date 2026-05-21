# SQLite Storage

TwinAgent AI includes a local SQLite storage layer for processed sensor readings and incidents.

---

## Purpose

SQLite storage prepares the project for:

- API-backed workflows
- dashboard/API integration
- local persistence
- future MQTT ingestion
- future database migration

---

## Database path

```text
data/processed/twinagent.db
```

---

## Tables

### `sensor_readings`

Stores processed sensor rows with:

- timestamp
- machine ID
- raw sensor values
- fault label
- machine state
- anomaly scores
- health score
- risk level
- maintenance urgency
- maintenance recommendation

### `incidents`

Stores incident records with:

- incident ID
- machine ID
- start/end time
- severity
- suspected fault
- anomaly scores
- contributing sensors JSON
- evidence JSON

### `metadata`

Stores simple database metadata such as schema version.

---

## Export command

Run:

```cmd
python scripts\export_to_sqlite.py
```

Expected output:

```text
TwinAgent AI SQLite export complete.
Sensor rows written: 3600
Incidents written: 1
Latest machine state: normal
Latest health score: 100
Latest risk level: healthy
```

---

## Repository API

The storage repository supports:

```text
initialize
clear_all
write_sensor_readings
write_incidents
get_sensor_row_count
get_incident_count
get_latest_machine_state
query_sensor_window
get_incident
list_incidents
```

---

## Why SQLite first?

SQLite is used because it is:

- simple
- local
- easy to test
- portable
- enough for an MVP demo
- suitable before adding a production database

---

## Current limitations

The current storage layer is not designed for high-throughput production ingestion. A future version can add:

- PostgreSQL
- TimescaleDB
- async database access
- streaming inserts from MQTT
- retention policies
- migrations
