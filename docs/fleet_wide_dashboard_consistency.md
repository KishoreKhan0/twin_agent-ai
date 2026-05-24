# Step 26 Fleet-Wide Dashboard Consistency

This patch makes the dashboard reflect fleet changes everywhere, not only in one tab.

## What changed

### Generator

The fleet generator now creates:

```text
12 machines
43200 sensor rows
20+ incidents expected
```

Long high/medium anomaly windows are split into operational incident episodes so
the dashboard has enough incidents for comparison questions.

### Dashboard

The dashboard is now fleet-aware across:

- sidebar artifact status
- hero badges
- overview tab
- incidents tab
- fleet tab
- copilot tab

If the dashboard is reading old fleet files, it shows a warning such as:

```text
Fleet artifacts look old. Current files show 3 machines and 6 incidents.
Run python scripts\generate_fleet_demo_data.py
```

### Copilot

The Copilot tab defaults to Global fleet with a new state key, so old Streamlit
session state should not keep it stuck on Specific incident.

## Required run order

```cmd
python -m pytest
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
python scripts\launch_dashboard.py
```

If Streamlit still shows old counts, stop it with Ctrl+C and restart after
regenerating fleet data.
