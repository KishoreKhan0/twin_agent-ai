# TwinAgent AI Fleet Triage Report

## Fleet scope

- Machines: 12
- Incidents: 80
- Time range: `2026-05-20T14:00:00` to `2026-05-21T03:49:59`

## Top maintenance priority

- Machine: `line6_motor2`
- Priority level: **critical**
- Priority score: **439.0**
- Recommended action: Stop machine if still active and perform immediate inspection.
- Reason: 10 incident(s), 6 high-severity incident(s), minimum health 25, 2318 anomaly row(s), suspected faults: bearing_wear, current_anomaly.

## Highest-priority incident

- Incident: `FLEET-M11-0004-S04`
- Machine: `line6_motor1`
- Severity: **high**
- Fault: **bearing_wear**
- Priority score: **148.4**
- Reason: high severity, suspected bearing_wear, max anomaly 0.7974, duration 299s, 4 contributing sensor(s).

## Machine triage

| Rank | Machine | Line | Priority | Score | Incidents | High incidents | Min health | Suspected faults | Recommended action |
|---:|---|---|---|---:|---:|---:|---:|---|---|
| 1 | line6_motor2 | line6 | critical | 439.0 | 10 | 6 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 2 | line5_motor2 | line5 | critical | 419.0 | 8 | 6 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 3 | line4_motor2 | line4 | critical | 419.0 | 8 | 6 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 4 | line3_motor2 | line3 | critical | 419.0 | 8 | 6 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 5 | line6_motor1 | line6 | critical | 399.8 | 8 | 5 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 6 | line2_motor2 | line2 | critical | 391.0 | 7 | 5 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 7 | line1_motor2 | line1 | critical | 388.35 | 7 | 5 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 8 | line4_motor1 | line4 | critical | 386.52 | 7 | 5 | 25 | bearing_wear, current_anomaly | Stop machine if still active and perform immediate inspection. |
| 9 | line3_motor1 | line3 | critical | 356.2 | 5 | 5 | 25 | bearing_wear | Stop machine if still active and perform immediate inspection. |
| 10 | line5_motor1 | line5 | critical | 355.88 | 5 | 5 | 25 | bearing_wear | Stop machine if still active and perform immediate inspection. |
| 11 | line1_motor1 | line1 | critical | 321.75 | 4 | 4 | 27 | bearing_wear | Stop machine if still active and perform immediate inspection. |
| 12 | line2_motor1 | line2 | critical | 269.57 | 3 | 2 | 31 | bearing_wear | Stop machine if still active and perform immediate inspection. |

## Incident triage

| Rank | Incident | Machine | Severity | Fault | Score | Duration | Max anomaly | Sensors |
|---:|---|---|---|---|---:|---:|---:|---|
| 1 | FLEET-M11-0004-S04 | line6_motor1 | high | bearing_wear | 148.4 | 299 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 2 | FLEET-M11-0004-S02 | line6_motor1 | high | bearing_wear | 148.4 | 299 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 3 | FLEET-M04-0003-S04 | line2_motor2 | high | bearing_wear | 148.4 | 299 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 4 | FLEET-M04-0003-S02 | line2_motor2 | high | bearing_wear | 148.4 | 299 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 5 | FLEET-M11-0004-S05 | line6_motor1 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 6 | FLEET-M11-0004-S03 | line6_motor1 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 7 | FLEET-M11-0004-S01 | line6_motor1 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 8 | FLEET-M04-0003-S05 | line2_motor2 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 9 | FLEET-M04-0003-S03 | line2_motor2 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 10 | FLEET-M04-0003-S01 | line2_motor2 | high | bearing_wear | 148.39 | 298 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 11 | FLEET-M02-0003-S05 | line1_motor2 | high | bearing_wear | 148.33 | 291 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 12 | FLEET-M02-0003-S04 | line1_motor2 | high | bearing_wear | 148.33 | 291 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 13 | FLEET-M02-0003-S03 | line1_motor2 | high | bearing_wear | 148.33 | 291 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 14 | FLEET-M02-0003-S02 | line1_motor2 | high | bearing_wear | 148.33 | 291 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 15 | FLEET-M02-0003-S01 | line1_motor2 | high | bearing_wear | 148.33 | 291 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 16 | FLEET-M12-0003-S06 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 17 | FLEET-M12-0003-S05 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 18 | FLEET-M12-0003-S04 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 19 | FLEET-M12-0003-S03 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 20 | FLEET-M12-0003-S02 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 21 | FLEET-M12-0003-S01 | line6_motor2 | high | bearing_wear | 148.27 | 283 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 22 | FLEET-M10-0003-S05 | line5_motor2 | high | bearing_wear | 148.12 | 265 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 23 | FLEET-M10-0003-S02 | line5_motor2 | high | bearing_wear | 148.12 | 265 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 24 | FLEET-M10-0003-S06 | line5_motor2 | high | bearing_wear | 148.11 | 264 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 25 | FLEET-M10-0003-S04 | line5_motor2 | high | bearing_wear | 148.11 | 264 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 26 | FLEET-M10-0003-S03 | line5_motor2 | high | bearing_wear | 148.11 | 264 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 27 | FLEET-M10-0003-S01 | line5_motor2 | high | bearing_wear | 148.11 | 264 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 28 | FLEET-M08-0003-S06 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 29 | FLEET-M08-0003-S05 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 30 | FLEET-M08-0003-S04 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 31 | FLEET-M08-0003-S03 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 32 | FLEET-M08-0003-S02 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 33 | FLEET-M08-0003-S01 | line4_motor2 | high | bearing_wear | 148.07 | 259 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 34 | FLEET-M07-0003-S05 | line4_motor1 | high | bearing_wear | 148.03 | 254 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 35 | FLEET-M07-0003-S03 | line4_motor1 | high | bearing_wear | 148.03 | 254 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 36 | FLEET-M07-0003-S01 | line4_motor1 | high | bearing_wear | 148.03 | 254 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 37 | FLEET-M07-0003-S04 | line4_motor1 | high | bearing_wear | 148.02 | 253 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 38 | FLEET-M07-0003-S02 | line4_motor1 | high | bearing_wear | 148.02 | 253 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 39 | FLEET-M09-0001-S05 | line5_motor1 | high | bearing_wear | 148.0 | 251 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 40 | FLEET-M09-0001-S04 | line5_motor1 | high | bearing_wear | 148.0 | 251 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 41 | FLEET-M09-0001-S03 | line5_motor1 | high | bearing_wear | 148.0 | 251 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 42 | FLEET-M09-0001-S02 | line5_motor1 | high | bearing_wear | 148.0 | 251 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 43 | FLEET-M09-0001-S01 | line5_motor1 | high | bearing_wear | 148.0 | 251 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 44 | FLEET-M06-0003-S06 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 45 | FLEET-M06-0003-S05 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 46 | FLEET-M06-0003-S04 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 47 | FLEET-M06-0003-S03 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 48 | FLEET-M06-0003-S02 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 49 | FLEET-M06-0003-S01 | line3_motor2 | high | bearing_wear | 147.99 | 250 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 50 | FLEET-M05-0001-S05 | line3_motor1 | high | bearing_wear | 147.98 | 248 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 51 | FLEET-M05-0001-S04 | line3_motor1 | high | bearing_wear | 147.98 | 249 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 52 | FLEET-M05-0001-S03 | line3_motor1 | high | bearing_wear | 147.98 | 248 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 53 | FLEET-M05-0001-S02 | line3_motor1 | high | bearing_wear | 147.98 | 249 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 54 | FLEET-M05-0001-S01 | line3_motor1 | high | bearing_wear | 147.98 | 248 | 0.7974 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 55 | FLEET-M01-0001-S03 | line1_motor1 | high | bearing_wear | 146.8 | 295 | 0.7526 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 56 | FLEET-M01-0001-S04 | line1_motor1 | high | bearing_wear | 146.79 | 294 | 0.7526 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 57 | FLEET-M01-0001-S02 | line1_motor1 | high | bearing_wear | 146.79 | 294 | 0.7526 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 58 | FLEET-M01-0001-S01 | line1_motor1 | high | bearing_wear | 146.79 | 294 | 0.7526 | current_a, temperature_c, throughput_units_min, vibration_mm_s |
| 59 | FLEET-M03-0001-S02 | line2_motor1 | high | bearing_wear | 140.9 | 288 | 0.7001 | current_a, temperature_c, vibration_mm_s |
| 60 | FLEET-M03-0001-S01 | line2_motor1 | high | bearing_wear | 140.9 | 288 | 0.7001 | current_a, temperature_c, vibration_mm_s |
| 61 | FLEET-M10-0001 | line5_motor2 | medium | bearing_wear | 116.42 | 407 | 0.6864 | current_a, temperature_c, vibration_mm_s |
| 62 | FLEET-M12-0001-S02 | line6_motor2 | medium | bearing_wear | 115.33 | 277 | 0.6864 | current_a, temperature_c, vibration_mm_s |
| 63 | FLEET-M12-0001-S01 | line6_motor2 | medium | bearing_wear | 115.32 | 276 | 0.6864 | current_a, temperature_c, vibration_mm_s |
| 64 | FLEET-M03-0002 | line2_motor1 | medium | bearing_wear | 113.73 | 310 | 0.6327 | temperature_c, throughput_units_min, vibration_mm_s |
| 65 | FLEET-M10-0002 | line5_motor2 | medium | current_anomaly | 97.81 | 398 | 0.6142 | current_a, vibration_mm_s |
| 66 | FLEET-M08-0001 | line4_motor2 | medium | current_anomaly | 97.36 | 343 | 0.6142 | current_a, vibration_mm_s |
| 67 | FLEET-M12-0002-S02 | line6_motor2 | medium | current_anomaly | 96.26 | 211 | 0.6142 | current_a, vibration_mm_s |
| 68 | FLEET-M12-0002-S01 | line6_motor2 | medium | current_anomaly | 96.25 | 210 | 0.6142 | current_a, vibration_mm_s |
| 69 | FLEET-M08-0002 | line4_motor2 | medium | current_anomaly | 90.61 | 351 | 0.5338 | current_a |
| 70 | FLEET-M06-0001 | line3_motor2 | medium | current_anomaly | 90.4 | 326 | 0.5338 | current_a |
| 71 | FLEET-M06-0002 | line3_motor2 | medium | current_anomaly | 90.29 | 313 | 0.5338 | current_a |
| 72 | FLEET-M04-0001 | line2_motor2 | medium | current_anomaly | 88.85 | 140 | 0.5338 | current_a |
| 73 | FLEET-M11-0001 | line6_motor1 | medium | current_anomaly | 88.44 | 91 | 0.5338 | current_a |
| 74 | FLEET-M04-0002 | line2_motor2 | low | current_anomaly | 56.99 | 261 | 0.3091 | current_a |
| 75 | FLEET-M11-0002 | line6_motor1 | low | current_anomaly | 55.54 | 87 | 0.3091 | current_a |
| 76 | FLEET-M02-0002 | line1_motor2 | low | current_anomaly | 55.19 | 44 | 0.3091 | current_a |
| 77 | FLEET-M07-0002 | line4_motor1 | low | current_anomaly | 55.06 | 29 | 0.3091 | current_a |
| 78 | FLEET-M02-0001 | line1_motor2 | low | current_anomaly | 55.04 | 27 | 0.3091 | current_a |
| 79 | FLEET-M11-0003 | line6_motor1 | low | current_anomaly | 55.02 | 24 | 0.3091 | current_a |
| 80 | FLEET-M07-0001 | line4_motor1 | low | current_anomaly | 55.02 | 24 | 0.3091 | current_a |
