# TwinAgent AI Evaluation Report

## Dataset summary

- Machine ID: `line1_motor1`
- Time range: `2026-05-20T14:00:00` to `2026-05-20T14:59:59`
- Total rows: **3600**
- Fault rows: **1320**
- Anomaly rows: **934**
- Incidents: **1**

## Binary anomaly detection metrics

| Metric | Value |
|---|---:|
| Precision | 1.0 |
| Recall | 0.7076 |
| F1 score | 0.8287 |
| Accuracy | 0.8928 |
| False positive rate | 0.0 |
| True positive | 934 |
| False positive | 0 |
| True negative | 2280 |
| False negative | 386 |

## Detection delay

- Fault episodes: **1**
- Detected episodes: **1**
- Missed episodes: **0**
- Mean detection delay: **142.0 seconds**
- Max detection delay: **142.0 seconds**

## Incident overlap

- Incident overlap score: **0.8924**
- Ground-truth fault rows: **1320**
- Incident-window rows: **1178**
- Overlap rows: **1178**

## Incident-level diagnosis

- Evaluated incidents: **1**
- Correct incidents: **1**
- Incident diagnosis accuracy: **1.0**

| Incident | Predicted fault | Ground-truth faults | Correct |
|---|---|---|---|
| INC-0001 | bearing_wear | bearing_wear, belt_misalignment, overheating | True |

## Row-level suspected-fault alignment

- Evaluated anomaly rows inside fault windows: **934**
- Row alignment accuracy: **0.1852**

| Ground-truth fault group | Predicted fault | Count |
|---|---|---:|
| bearing_wear | vibration_anomaly | 550 |
| bearing_wear+overheating | bearing_wear | 58 |
| bearing_wear+overheating | vibration_anomaly | 2 |
| belt_misalignment | vibration_anomaly | 60 |
| belt_misalignment+overheating | bearing_wear | 149 |
| belt_misalignment+overheating | overheating | 85 |
| belt_misalignment+overheating | belt_misalignment | 4 |
| overheating | overheating | 26 |

## Notes

- These metrics are evaluated against synthetic ground-truth fault labels.
- Incident-level diagnosis is the most relevant diagnosis metric for the current MVP because the copilot explains incidents.
- Row-level suspected-fault alignment is stricter and can be lower during overlapping or evolving fault windows.
- The detector is an interpretable prototype using threshold-based anomaly logic.
- The results should not be described as real-world predictive-maintenance accuracy.
