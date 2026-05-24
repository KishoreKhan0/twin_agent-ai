# Maintenance Work Orders

Step 28 converts incident analytics into technician-ready work orders.

## What it adds

- Work-order generation from local incidents
- Work-order generation from fleet incidents
- Priority levels: P1, P2, P3, P4
- Due windows
- Estimated effort
- Recommended action
- Safety note
- Technician checklist
- Markdown and JSON export
- Dashboard Work Orders tab

## Run

```cmd
python scripts\export_work_orders.py
```

Generated files:

```text
data/reports/local_work_orders.json
data/reports/local_work_orders.md
data/fleet/reports/fleet_work_orders.json
data/fleet/reports/fleet_work_orders.md
```

## Dashboard

The dashboard now includes:

```text
🛠️ Work Orders
```

with:

- Local work orders
- Fleet work orders
- P1/P2 queue metrics
- affected machines
- selected work-order checklist
