# Full Backend Pipeline Orchestrator

Step 33 adds one command to run the full TwinAgent AI backend pipeline.

No dashboard changes.

## Why this exists

Before this step, the project required many manual commands:

```cmd
python scripts\bootstrap_demo_data.py
python scripts\train_fault_classifier.py
python scripts\predict_faults.py
python scripts\explain_fault_classifier.py
python scripts\enrich_incidents_with_ml.py
python scripts\reconcile_incident_diagnoses.py
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
python scripts\export_work_orders.py
```

Now the backend pipeline can be run with:

```cmd
python scripts\run_full_pipeline.py
```

## What it runs

Default full run:

1. Bootstrap local demo data
2. Train ML fault classifier
3. Predict fault windows
4. Export ML explainability
5. Enrich incidents with ML diagnosis
6. Reconcile rule/ML diagnosis
7. Generate fleet demo data
8. Export global fleet analysis
9. Export fleet triage
10. Export work orders using reconciled local diagnoses

## Useful options

Run tests first:

```cmd
python scripts\run_full_pipeline.py --include-tests
```

Run local-only pipeline:

```cmd
python scripts\run_full_pipeline.py --local-only
```

Continue even if a step fails:

```cmd
python scripts\run_full_pipeline.py --continue-on-failure
```

## Outputs

```text
data/reports/pipeline_run_summary.json
data/reports/pipeline_run_summary.md
```

The summary includes:

- step statuses
- missing artifacts if any
- local incident count
- reconciled incident count
- fleet machine/incident counts
- ML metrics
- work-order counts
