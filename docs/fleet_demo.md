# Fleet Demo

TwinAgent AI now includes an optional multi-machine fleet demo generator.

This does not replace the original single-machine pipeline. It adds a separate
fleet-level dataset under:

```text
data/fleet/
```

---

## Run

```cmd
python scripts\generate_fleet_demo_data.py
```

Expected output includes:

```text
TwinAgent AI fleet demo generation complete.
Machines generated: 3
Sensor rows written: 10800
```

---

## Generated files

```text
data/fleet/generated/fleet_sensor_data.csv
data/fleet/processed/fleet_sensor_data_with_anomalies.csv
data/fleet/processed/twinagent_fleet.db
data/fleet/incidents/fleet_incidents.json
data/fleet/reports/fleet_summary.json
data/fleet/reports/fleet_summary.md
```

---

## Machines

The fleet demo creates:

```text
line1_motor1
line1_motor2
line2_motor1
```

Each machine uses the same base simulator, but receives different identifiers,
time offsets, sensor offsets, and random seeds.

---

## Why this matters

The original MVP proves the system on one machine. The fleet demo makes the
project more realistic for industrial settings where teams monitor multiple
assets, compare machine health, and triage incidents across production lines.

---

## Current scope

This is a data-generation and storage extension. The original dashboard still
uses the main single-machine files unless separately extended to load fleet data.
