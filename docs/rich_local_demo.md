# Rich Local Demo

This step expands the local/single-machine demo.

Previously, the local dashboard showed only one incident because the local demo
still used the original compact 60-minute config.

The new local demo uses:

```text
configs/local_demo_config.yaml
```

Expected local output:

```text
21600 sensor rows
10+ operational incidents
```

The fleet demo remains separate and still generates larger fleet-wide data.

## Files updated

- `configs/local_demo_config.yaml`
- `scripts/generate_synthetic_data.py`
- `scripts/run_anomaly_detection.py`
- `scripts/bootstrap_demo_data.py`
- `src/twinagent/analytics/incident_segments.py`
- `src/twinagent/dashboard/streamlit_app.py`

## Run

```cmd
python -m pytest
python scripts\bootstrap_demo_data.py
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
python scripts\launch_dashboard.py
```

## Dashboard behavior

The dashboard now warns when local files are old, for example:

```text
Local demo artifacts look old. Current local files show 3600 rows and 1 incident.
Run python scripts\bootstrap_demo_data.py
```
