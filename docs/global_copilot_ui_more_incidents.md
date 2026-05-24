# Global Copilot UI + Larger Fleet

This patch fixes the dashboard layout and expands the default fleet.

## What changed

### Copilot tab

All question-answer behavior now lives in the Copilot tab.

Default scope:

```text
Global fleet
```

This answers across all machines and all fleet incidents.

Specific incident mode still exists, but the incident selector only appears after switching to:

```text
Specific incident
```

### Fleet tab

The Fleet tab is now monitoring and drill-down only:

- fleet KPIs
- machine table
- fleet incidents table
- machine sensor charts
- machine health chart
- anomaly chart

No Q&A section is shown there.

### Incidents tab

The Incidents tab now shows:

- single-machine incidents
- fleet incidents
- filters by machine, severity, and fault

### More incidents

The fleet generator now creates 10 machines:

```text
line1_motor1, line1_motor2
line2_motor1, line2_motor2
line3_motor1, line3_motor2
line4_motor1, line4_motor2
line5_motor1, line5_motor2
```

Expected rows:

```text
36000
```

Expected incident count:

```text
10+
```

## Run

```cmd
python -m pytest
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
python scripts\launch_dashboard.py
```
