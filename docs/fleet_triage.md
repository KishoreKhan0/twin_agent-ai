# Fleet Triage

Step 23 adds deterministic fleet-level maintenance triage.

It ranks:

- machines by maintenance priority
- incidents by urgency
- top machine to inspect first
- top incident to review first

The triage system is deterministic and explainable. It does not require AI or API billing.

---

## Run

```cmd
python scripts\generate_fleet_demo_data.py
python scripts\export_fleet_triage.py
```

Generated reports:

```text
data/fleet/reports/fleet_triage.json
data/fleet/reports/fleet_triage.md
```

---

## What the score considers

Machine priority considers:

- incident count
- high-severity incident count
- minimum health score
- anomaly row count
- suspected fault diversity
- incident priority scores

Incident priority considers:

- severity
- suspected fault
- max anomaly score
- duration
- number of contributing sensors

---

## Why this matters

For an industrial fleet, the operator does not only need to know that incidents exist. They need to know what to inspect first.

Fleet triage turns raw fleet incidents into maintenance priority decisions.
