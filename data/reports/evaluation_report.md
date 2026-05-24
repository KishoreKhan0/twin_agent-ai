# TwinAgent AI Evaluation Report

## Dataset summary

- Machine ID: `line1_motor1`
- Time range: `2026-05-20T14:00:00` to `2026-05-20T19:59:59`
- Total rows: **21600**
- Fault rows: **7200**
- Anomaly rows: **5158**
- Incidents: **24**

## Binary anomaly detection metrics

| Metric | Value |
|---|---:|
| Precision | 0.9969 |
| Recall | 0.7142 |
| F1 score | 0.8322 |
| Accuracy | 0.904 |
| False positive rate | 0.0011 |
| True positive | 5142 |
| False positive | 16 |
| True negative | 14384 |
| False negative | 2058 |

## Detection delay

- Fault episodes: **12**
- Detected episodes: **12**
- Missed episodes: **0**
- Mean detection delay: **95.33 seconds**
- Max detection delay: **350.0 seconds**

## Incident overlap

- Incident overlap score: **0.7399**
- Ground-truth fault rows: **7200**
- Incident-window rows: **5487**
- Overlap rows: **5395**

## Incident-level diagnosis

- Evaluated incidents: **24**
- Correct incidents: **9**
- Incident diagnosis accuracy: **0.375**

| Incident | Predicted fault | Ground-truth faults | Correct |
|---|---|---|---|
| INC-0001 | vibration_anomaly | bearing_wear | False |
| INC-0002 | vibration_anomaly | bearing_wear | False |
| INC-0003 | vibration_anomaly | bearing_wear | False |
| INC-0004 | overheating | overheating | True |
| INC-0005 | vibration_anomaly | belt_misalignment | False |
| INC-0006 | overheating | motor_overload | False |
| INC-0007 | throughput_anomaly |  | False |
| INC-0008 | vibration_anomaly | bearing_wear | False |
| INC-0009 | vibration_anomaly | bearing_wear | False |
| INC-0010 | vibration_anomaly | bearing_wear | False |
| INC-0011 | overheating | cooling_failure | False |
| INC-0012 | vibration_anomaly | belt_misalignment | False |
| INC-0013 | vibration_anomaly | belt_misalignment | False |
| INC-0014 | overheating | overheating | True |
| INC-0015 | bearing_wear | bearing_wear | True |
| INC-0016 | bearing_wear | bearing_wear | True |
| INC-0017 | bearing_wear | bearing_wear | True |
| INC-0018 | bearing_wear | bearing_wear | True |
| INC-0019 | throughput_anomaly |  | False |
| INC-0020 | overheating | motor_overload | False |
| INC-0021 | overheating | motor_overload | False |
| INC-0022 | belt_misalignment | belt_misalignment | True |
| INC-0023 | belt_misalignment | belt_misalignment | True |
| INC-0024 | belt_misalignment | belt_misalignment | True |

## Row-level suspected-fault alignment

- Evaluated anomaly rows inside fault windows: **5142**
- Row alignment accuracy: **0.2981**

| Ground-truth fault group | Predicted fault | Count |
|---|---|---:|
| bearing_wear | vibration_anomaly | 1742 |
| bearing_wear | bearing_wear | 73 |
| belt_misalignment | vibration_anomaly | 1465 |
| belt_misalignment | belt_misalignment | 11 |
| cooling_failure | overheating | 368 |
| cooling_failure | motor_overload | 1 |
| motor_overload | motor_overload | 800 |
| overheating | overheating | 649 |
| overheating | motor_overload | 32 |
| sensor_drift | motor_overload | 1 |

## Notes

- These metrics are evaluated against synthetic ground-truth fault labels.
- Incident-level diagnosis is the most relevant diagnosis metric for the current MVP because the copilot explains incidents.
- Row-level suspected-fault alignment is stricter and can be lower during overlapping or evolving fault windows.
- The detector is an interpretable prototype using threshold-based anomaly logic.
- The results should not be described as real-world predictive-maintenance accuracy.
