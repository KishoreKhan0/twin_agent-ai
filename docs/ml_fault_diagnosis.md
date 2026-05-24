# ML Fault Diagnosis Engine

Step 29 adds a backend-only ML pipeline for fault diagnosis.

No dashboard changes.

## What it does

The classifier learns fault patterns from time-windowed sensor features.

Pipeline:

```text
processed sensor data
    -> windowed feature extraction
    -> supervised fault classifier
    -> model artifact
    -> metrics report
    -> fault prediction CSV
```

## Commands

```cmd
python scripts\bootstrap_demo_data.py
python scripts\train_fault_classifier.py
python scripts\predict_faults.py
```

## Outputs

```text
models/fault_classifier.joblib
models/fault_classifier_metrics.json
models/fault_classifier_report.md
data/processed/sensor_data_with_fault_predictions.csv
```

## Features

For each sensor window, the system computes:

- mean
- standard deviation
- min
- max
- range
- last value
- slope

The target label is the dominant non-normal fault in the window.

## Why it matters

This moves TwinAgent AI beyond deterministic rules and adds a reusable ML fault
diagnosis layer suitable for experimentation, benchmarking, and future model
improvements.
