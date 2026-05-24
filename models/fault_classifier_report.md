# TwinAgent AI Fault Classifier Report

## Summary

- Windows: 359
- Train windows: 269
- Test windows: 90
- Features: 70
- Classes: 7
- Accuracy: 0.9333
- Macro F1: 0.7888
- Weighted F1: 0.9332

## Classes

- `bearing_wear`
- `belt_misalignment`
- `cooling_failure`
- `motor_overload`
- `normal`
- `overheating`
- `sensor_drift`

## Per-class scores

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| bearing_wear | 1.0 | 1.0 | 1.0 | 10 |
| belt_misalignment | 1.0 | 1.0 | 1.0 | 8 |
| cooling_failure | 0.25 | 0.3333 | 0.2857 | 3 |
| motor_overload | 1.0 | 1.0 | 1.0 | 4 |
| normal | 0.9828 | 1.0 | 0.9913 | 57 |
| overheating | 0.5 | 0.4 | 0.4444 | 5 |
| sensor_drift | 1.0 | 0.6667 | 0.8 | 3 |
