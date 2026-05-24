# Fleet Dashboard

Step 22 adds a Fleet tab to the Streamlit dashboard.

The tab loads optional fleet artifacts from:

```text
data/fleet/
```

If the files do not exist, the dashboard stays usable and shows the command:

```cmd
python scripts\generate_fleet_demo_data.py
```

---

## Fleet tab features

- Fleet overview KPIs
- Machine health table
- Fleet incident table
- Machine selector
- Per-machine sensor timeline
- Per-machine health chart
- Per-machine anomaly score chart
- Incidents filtered by machine

---

## Required files

```text
data/fleet/processed/fleet_sensor_data_with_anomalies.csv
data/fleet/incidents/fleet_incidents.json
data/fleet/reports/fleet_summary.json
```

---

## Workflow

```cmd
python scripts\generate_fleet_demo_data.py
python scripts\launch_dashboard.py
```
