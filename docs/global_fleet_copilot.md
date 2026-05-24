# Global Fleet Copilot

Step 24 expands the fleet demo and adds global incident intelligence.

The fleet copilot no longer requires selecting one incident. It answers across
all fleet incidents.

---

## Example questions

```text
Which machine should maintenance inspect first?
Compare bearing wear incidents.
Show current anomaly incidents.
Why is line1_motor2 critical?
Which issue appears most often?
Show the fleet incident timeline.
```

---

## Reports

Run:

```cmd
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
```

Generated files:

```text
data/fleet/reports/global_fleet_analysis.json
data/fleet/reports/global_fleet_analysis.md
data/fleet/reports/fleet_triage.json
data/fleet/reports/fleet_triage.md
```

---

## Why this matters

This moves the project from incident-by-incident Q&A to fleet-level operations:

- repeated fault analysis
- machine comparison
- global incident timeline
- fault pattern aggregation
- maintenance prioritization across machines
