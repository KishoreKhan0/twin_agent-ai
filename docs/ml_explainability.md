# ML Explainability and Error Analysis

Step 30 adds backend-only ML explainability.

No dashboard changes.

## Why this exists

The fault classifier now works, but an ML model should not be a black box.
This step exports artifacts that explain what the model uses and where it is weak.

## Commands

Run after training and prediction:

```cmd
python scripts\explain_fault_classifier.py
```

## Outputs

```text
models/fault_classifier_feature_importance.csv
models/fault_classifier_error_analysis.json
models/fault_classifier_model_card.md
data/processed/fault_prediction_audit.csv
```

## What each file means

### Feature importance CSV

Ranks sensor-window features by Random Forest importance.

Examples:

```text
temperature_c_max
vibration_mm_s_slope
current_a_mean
health_score_min
anomaly_score_max
```

### Error analysis JSON

Summarizes:

- prediction window count
- low-confidence count
- predicted fault counts
- incorrect count if target labels are available
- confusion pairs

### Model card

Human-readable ML summary:

- training metrics
- weak classes
- top features
- limitations
- audit notes

### Prediction audit CSV

Window-by-window audit table with:

- target fault
- predicted fault
- confidence
- correctness
- low-confidence flag
