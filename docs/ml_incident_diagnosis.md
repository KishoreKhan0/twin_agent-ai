# ML-Assisted Incident Diagnosis Integration

Step 31 connects the trained ML classifier back into the incident workflow.

## What it does

For each incident, the system finds overlapping ML prediction windows from:

```text
data/processed/sensor_data_with_fault_predictions.csv
```

Then it adds ML diagnosis fields to the incident record.

## Added fields

```json
{
  "ml_predicted_fault": "bearing_wear",
  "ml_confidence": 0.87,
  "diagnosis_agreement": true,
  "ml_low_confidence": false,
  "ml_matched_window_count": 3,
  "ml_matched_window_start": "2026-05-20 14:10:00",
  "ml_matched_window_end": "2026-05-20 14:13:00",
  "ml_prediction_distribution": {
    "bearing_wear": 3
  },
  "ml_diagnosis_note": "Rule diagnosis and ML diagnosis agree..."
}
```

## Commands

Run after training and prediction:

```cmd
python scripts\enrich_incidents_with_ml.py
```

## Outputs

```text
data/incidents/incidents_with_ml.json
data/reports/ml_incident_diagnosis_report.md
```

## Why this matters

The ML model is no longer standalone. It now becomes a second opinion inside the
actual incident workflow.

This allows later API/report/copilot/work-order layers to use:

- rule diagnosis
- ML diagnosis
- confidence
- agreement/disagreement
- low-confidence flags
