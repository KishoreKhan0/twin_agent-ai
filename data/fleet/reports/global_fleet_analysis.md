# TwinAgent AI Global Fleet Incident Analysis

## Fleet scope

- Machines: 12
- Sensor rows: 43200
- Incidents: 80

## Fault patterns

| Fault | Incidents | Machines | Severity counts | Avg duration | Max anomaly | Common sensors |
|---|---:|---|---|---:|---:|---|
| bearing_wear | 64 | line1_motor1, line1_motor2, line2_motor1, line2_motor2, line3_motor1, line3_motor2, line4_motor1, line4_motor2, line5_motor1, line5_motor2, line6_motor1, line6_motor2 | {'high': 60, 'medium': 4} | 274.45 | 0.7974 | temperature_c, vibration_mm_s, current_a, throughput_units_min |
| current_anomaly | 16 | line1_motor2, line2_motor2, line3_motor2, line4_motor1, line4_motor2, line5_motor2, line6_motor1, line6_motor2 | {'low': 7, 'medium': 9} | 179.94 | 0.6142 | current_a, vibration_mm_s |

## Example global questions

- Which machine should maintenance inspect first?
- Compare bearing wear incidents.
- Which issue appears most often?
- Show current anomaly incidents.
