# TwinAgent AI ML-Assisted Incident Diagnosis

## Summary

- Incidents analyzed: 24
- Incidents with ML windows: 24
- Rule/ML disagreements: 15
- Low-confidence ML diagnoses: 0

## Incident diagnosis table

| Incident | Rule fault | ML fault | Confidence | Agreement | Low confidence | Matched windows |
|---|---|---|---:|---|---|---:|
| INC-0001 | vibration_anomaly | bearing_wear | 0.9592 | False | False | 5 |
| INC-0002 | vibration_anomaly | bearing_wear | 0.9936 | False | False | 5 |
| INC-0003 | vibration_anomaly | bearing_wear | 0.875 | False | False | 4 |
| INC-0004 | overheating | overheating | 0.6984 | True | False | 8 |
| INC-0005 | vibration_anomaly | belt_misalignment | 0.9164 | False | False | 9 |
| INC-0006 | overheating | motor_overload | 0.929 | False | False | 8 |
| INC-0007 | throughput_anomaly | normal | 0.99 | False | False | 3 |
| INC-0008 | vibration_anomaly | bearing_wear | 0.9488 | False | False | 5 |
| INC-0009 | vibration_anomaly | bearing_wear | 0.958 | False | False | 6 |
| INC-0010 | vibration_anomaly | bearing_wear | 0.8872 | False | False | 5 |
| INC-0011 | overheating | cooling_failure | 0.8133 | False | False | 8 |
| INC-0012 | vibration_anomaly | belt_misalignment | 0.9687 | False | False | 6 |
| INC-0013 | vibration_anomaly | belt_misalignment | 0.9368 | False | False | 5 |
| INC-0014 | overheating | overheating | 0.8697 | True | False | 7 |
| INC-0015 | bearing_wear | bearing_wear | 0.9672 | True | False | 5 |
| INC-0016 | bearing_wear | bearing_wear | 0.9664 | True | False | 5 |
| INC-0017 | bearing_wear | bearing_wear | 0.9584 | True | False | 5 |
| INC-0018 | bearing_wear | bearing_wear | 0.8856 | True | False | 5 |
| INC-0019 | throughput_anomaly | normal | 0.986 | False | False | 3 |
| INC-0020 | overheating | motor_overload | 0.872 | False | False | 6 |
| INC-0021 | overheating | motor_overload | 0.932 | False | False | 5 |
| INC-0022 | belt_misalignment | belt_misalignment | 0.8712 | True | False | 5 |
| INC-0023 | belt_misalignment | belt_misalignment | 0.948 | True | False | 5 |
| INC-0024 | belt_misalignment | belt_misalignment | 0.8616 | True | False | 5 |

## Review notes

- `INC-0001`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.96. Review disagreement and compare contributing sensors.
- `INC-0002`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.99. Review disagreement and compare contributing sensors.
- `INC-0003`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.88. Review disagreement and compare contributing sensors.
- `INC-0004`: Rule diagnosis and ML diagnosis agree on overheating. ML confidence is 0.70 across 8 matched window(s).
- `INC-0005`: Rule diagnosis is vibration_anomaly, while ML predicts belt_misalignment with confidence 0.92. Review disagreement and compare contributing sensors.
- `INC-0006`: Rule diagnosis is overheating, while ML predicts motor_overload with confidence 0.93. Review disagreement and compare contributing sensors.
- `INC-0007`: Rule diagnosis is throughput_anomaly, while ML predicts normal with confidence 0.99. Review disagreement and compare contributing sensors.
- `INC-0008`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.95. Review disagreement and compare contributing sensors.
- `INC-0009`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.96. Review disagreement and compare contributing sensors.
- `INC-0010`: Rule diagnosis is vibration_anomaly, while ML predicts bearing_wear with confidence 0.89. Review disagreement and compare contributing sensors.
- `INC-0011`: Rule diagnosis is overheating, while ML predicts cooling_failure with confidence 0.81. Review disagreement and compare contributing sensors.
- `INC-0012`: Rule diagnosis is vibration_anomaly, while ML predicts belt_misalignment with confidence 0.97. Review disagreement and compare contributing sensors.
- `INC-0013`: Rule diagnosis is vibration_anomaly, while ML predicts belt_misalignment with confidence 0.94. Review disagreement and compare contributing sensors.
- `INC-0014`: Rule diagnosis and ML diagnosis agree on overheating. ML confidence is 0.87 across 7 matched window(s).
- `INC-0015`: Rule diagnosis and ML diagnosis agree on bearing_wear. ML confidence is 0.97 across 5 matched window(s).
- `INC-0016`: Rule diagnosis and ML diagnosis agree on bearing_wear. ML confidence is 0.97 across 5 matched window(s).
- `INC-0017`: Rule diagnosis and ML diagnosis agree on bearing_wear. ML confidence is 0.96 across 5 matched window(s).
- `INC-0018`: Rule diagnosis and ML diagnosis agree on bearing_wear. ML confidence is 0.89 across 5 matched window(s).
- `INC-0019`: Rule diagnosis is throughput_anomaly, while ML predicts normal with confidence 0.99. Review disagreement and compare contributing sensors.
- `INC-0020`: Rule diagnosis is overheating, while ML predicts motor_overload with confidence 0.87. Review disagreement and compare contributing sensors.
- `INC-0021`: Rule diagnosis is overheating, while ML predicts motor_overload with confidence 0.93. Review disagreement and compare contributing sensors.
- `INC-0022`: Rule diagnosis and ML diagnosis agree on belt_misalignment. ML confidence is 0.87 across 5 matched window(s).
- `INC-0023`: Rule diagnosis and ML diagnosis agree on belt_misalignment. ML confidence is 0.95 across 5 matched window(s).
- `INC-0024`: Rule diagnosis and ML diagnosis agree on belt_misalignment. ML confidence is 0.86 across 5 matched window(s).
