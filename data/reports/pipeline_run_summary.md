# TwinAgent AI Pipeline Run Summary

## Status

- Status: **passed**
- Duration: **32.596s**
- Project root: `C:\Users\KISHORE KHAN\Desktop\Projects\twinagent-ai`

## Steps

| Step | Status | Duration | Missing outputs |
|---|---|---:|---|
| bootstrap_local_demo_data | passed | 5.663s | none |
| train_fault_classifier | passed | 5.078s | none |
| predict_fault_windows | passed | 4.402s | none |
| explain_fault_classifier | passed | 2.419s | none |
| enrich_incidents_with_ml | passed | 2.353s | none |
| reconcile_incident_diagnoses | passed | 2.615s | none |
| generate_fleet_demo_data | passed | 9.666s | none |
| export_global_fleet_analysis | passed | 0.136s | none |
| export_fleet_triage | passed | 0.112s | none |
| export_work_orders | passed | 0.149s | none |

## Artifact summary

### local

- incident_count: `24`
- reconciled_incident_count: `24`

### fleet

- machine_count: `12`
- incident_count: `80`
- sensor_rows: `43200`

### ml

- window_count: `359`
- feature_count: `70`
- class_count: `7`
- accuracy: `0.9333`
- macro_f1: `0.7888`
- weighted_f1: `0.9332`

### reports

- local_work_orders: `24`
- fleet_work_orders: `80`
- pipeline_summary_json: `C:\Users\KISHORE KHAN\Desktop\Projects\twinagent-ai\data\reports\pipeline_run_summary.json`
- pipeline_summary_md: `C:\Users\KISHORE KHAN\Desktop\Projects\twinagent-ai\data\reports\pipeline_run_summary.md`
