# TwinAgent AI Maintenance Work Orders

## Queue summary

- Total work orders: 24
- Open P1: 4
- Open P2: 17
- Machines affected: 1
- Top priority machine: `line1_motor1`

## Work-order queue

| Work order | Incident | Machine | Priority | Severity | Fault | Due | Effort |
|---|---|---|---|---|---|---:|---:|
| LWO-00015 | INC-0015 | line1_motor1 | P1 | high | bearing_wear | 4h | 135m |
| LWO-00016 | INC-0016 | line1_motor1 | P1 | high | bearing_wear | 4h | 135m |
| LWO-00017 | INC-0017 | line1_motor1 | P1 | high | bearing_wear | 4h | 135m |
| LWO-00018 | INC-0018 | line1_motor1 | P1 | high | bearing_wear | 4h | 135m |
| LWO-00001 | INC-0001 | line1_motor1 | P2 | medium | bearing_wear | 24h | 95m |
| LWO-00002 | INC-0002 | line1_motor1 | P2 | medium | bearing_wear | 24h | 95m |
| LWO-00003 | INC-0003 | line1_motor1 | P2 | medium | bearing_wear | 24h | 95m |
| LWO-00004 | INC-0004 | line1_motor1 | P2 | medium | overheating | 24h | 100m |
| LWO-00006 | INC-0006 | line1_motor1 | P2 | medium | motor_overload | 24h | 100m |
| LWO-00008 | INC-0008 | line1_motor1 | P2 | medium | bearing_wear | 24h | 100m |
| LWO-00009 | INC-0009 | line1_motor1 | P2 | medium | bearing_wear | 24h | 100m |
| LWO-00010 | INC-0010 | line1_motor1 | P2 | medium | bearing_wear | 24h | 100m |
| LWO-00011 | INC-0011 | line1_motor1 | P2 | medium | overheating | 24h | 100m |
| LWO-00012 | INC-0012 | line1_motor1 | P2 | medium | belt_misalignment | 24h | 100m |
| LWO-00013 | INC-0013 | line1_motor1 | P2 | medium | belt_misalignment | 24h | 100m |
| LWO-00014 | INC-0014 | line1_motor1 | P2 | medium | overheating | 24h | 100m |
| LWO-00020 | INC-0020 | line1_motor1 | P2 | medium | motor_overload | 24h | 90m |
| LWO-00021 | INC-0021 | line1_motor1 | P2 | medium | motor_overload | 24h | 90m |
| LWO-00022 | INC-0022 | line1_motor1 | P2 | medium | belt_misalignment | 24h | 105m |
| LWO-00023 | INC-0023 | line1_motor1 | P2 | medium | belt_misalignment | 24h | 105m |
| LWO-00024 | INC-0024 | line1_motor1 | P2 | medium | belt_misalignment | 24h | 105m |
| LWO-00005 | INC-0005 | line1_motor1 | P3 | low | belt_misalignment | 72h | 85m |
| LWO-00007 | INC-0007 | line1_motor1 | P3 | low | throughput_anomaly | 72h | 40m |
| LWO-00019 | INC-0019 | line1_motor1 | P3 | low | throughput_anomaly | 72h | 40m |

## Detailed instructions

### LWO-00015 — line1_motor1

- Incident: `INC-0015`
- Priority: **P1**
- Severity: **high**
- Fault: **bearing_wear**
- Time window: `2026-05-20T18:56:21` → `2026-05-20T18:59:31`
- Due within: **4 hours**
- Estimated effort: **135 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: high incident with final diagnosis bearing_wear; duration 190s; max anomaly 0.7001; sensors: current_a, temperature_c, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=bearing_wear; ml=bearing_wear (0.9672).
- Safety note: Treat as urgent. Lock out/tag out before physical inspection if machine intervention is required.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00016 — line1_motor1

- Incident: `INC-0016`
- Priority: **P1**
- Severity: **high**
- Fault: **bearing_wear**
- Time window: `2026-05-20T18:59:31` → `2026-05-20T19:02:40`
- Due within: **4 hours**
- Estimated effort: **135 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: high incident with final diagnosis bearing_wear; duration 189s; max anomaly 0.7001; sensors: current_a, temperature_c, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=bearing_wear; ml=bearing_wear (0.9664).
- Safety note: Treat as urgent. Lock out/tag out before physical inspection if machine intervention is required.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00017 — line1_motor1

- Incident: `INC-0017`
- Priority: **P1**
- Severity: **high**
- Fault: **bearing_wear**
- Time window: `2026-05-20T19:02:40` → `2026-05-20T19:05:49`
- Due within: **4 hours**
- Estimated effort: **135 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: high incident with final diagnosis bearing_wear; duration 189s; max anomaly 0.7001; sensors: current_a, temperature_c, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=bearing_wear; ml=bearing_wear (0.9584).
- Safety note: Treat as urgent. Lock out/tag out before physical inspection if machine intervention is required.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00018 — line1_motor1

- Incident: `INC-0018`
- Priority: **P1**
- Severity: **high**
- Fault: **bearing_wear**
- Time window: `2026-05-20T19:05:49` → `2026-05-20T19:08:59`
- Due within: **4 hours**
- Estimated effort: **135 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: high incident with final diagnosis bearing_wear; duration 190s; max anomaly 0.7001; sensors: current_a, temperature_c, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=bearing_wear; ml=bearing_wear (0.8856).
- Safety note: Treat as urgent. Lock out/tag out before physical inspection if machine intervention is required.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00001 — line1_motor1

- Incident: `INC-0001`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T14:21:29` → `2026-05-20T14:24:19`
- Due within: **24 hours**
- Estimated effort: **95 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 170s; max anomaly 0.5662; sensors: vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.9592).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00002 — line1_motor1

- Incident: `INC-0002`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T14:24:19` → `2026-05-20T14:27:09`
- Due within: **24 hours**
- Estimated effort: **95 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 170s; max anomaly 0.5662; sensors: vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.9936).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00003 — line1_motor1

- Incident: `INC-0003`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T14:27:09` → `2026-05-20T14:29:59`
- Due within: **24 hours**
- Estimated effort: **95 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 170s; max anomaly 0.5662; sensors: vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.875).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00004 — line1_motor1

- Incident: `INC-0004`
- Priority: **P2**
- Severity: **medium**
- Fault: **overheating**
- Time window: `2026-05-20T14:48:24` → `2026-05-20T14:54:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect cooling path, motor load, ambient conditions, and electrical terminals before extended operation.
- Evidence: medium incident with final diagnosis overheating; duration 396s; max anomaly 0.5523; sensors: current_a, temperature_c. Diagnosis source: rule_ml_agreement; rule=overheating; ml=overheating (0.6984).
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Check cooling airflow and fan operation.
- [ ] Inspect motor surface temperature and thermal hot spots.
- [ ] Verify motor load and duty cycle during the incident.
- [ ] Inspect electrical terminals for loose or heated contacts.
- [ ] Confirm ambient temperature and ventilation conditions.

### LWO-00006 — line1_motor1

- Incident: `INC-0006`
- Priority: **P2**
- Severity: **medium**
- Fault: **motor_overload**
- Time window: `2026-05-20T15:45:01` → `2026-05-20T15:51:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect electrical current draw, mechanical loading, conveyor drag, and drive/VFD overload history.
- Evidence: medium incident with final diagnosis motor_overload; duration 419s; max anomaly 0.6061; sensors: current_a, temperature_c. Diagnosis source: ml_high_confidence_disagreement; rule=overheating; ml=motor_overload (0.929). Diagnosis requires review before closing the work order.
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Inspect motor current draw under production load.
- [ ] Check conveyor for mechanical jam, drag, or overloading.
- [ ] Review drive/VFD overload history and current limits.
- [ ] Verify belt tension and downstream blockage.
- [ ] Reduce load and retest current stability.

### LWO-00008 — line1_motor1

- Incident: `INC-0008`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T16:13:28` → `2026-05-20T16:16:58`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 210s; max anomaly 0.6278; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.9488).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00009 — line1_motor1

- Incident: `INC-0009`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T16:16:58` → `2026-05-20T16:20:29`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 211s; max anomaly 0.6278; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.958).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00010 — line1_motor1

- Incident: `INC-0010`
- Priority: **P2**
- Severity: **medium**
- Fault: **bearing_wear**
- Time window: `2026-05-20T16:20:29` → `2026-05-20T16:23:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Prioritize bearing inspection, lubrication review, vibration check, and replacement planning if trend persists.
- Evidence: medium incident with final diagnosis bearing_wear; duration 210s; max anomaly 0.6278; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=bearing_wear (0.8872).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect bearing housing for abnormal vibration and heat.
- [ ] Check lubrication condition and contamination.
- [ ] Review vibration trend around the incident window.
- [ ] Inspect shaft alignment and coupling condition.
- [ ] Plan bearing replacement if vibration remains elevated.

### LWO-00011 — line1_motor1

- Incident: `INC-0011`
- Priority: **P2**
- Severity: **medium**
- Fault: **overheating**
- Time window: `2026-05-20T16:47:27` → `2026-05-20T16:53:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect cooling path, motor load, ambient conditions, and electrical terminals before extended operation.
- Evidence: medium incident with final diagnosis overheating; duration 393s; max anomaly 0.5523; sensors: current_a, temperature_c. Diagnosis source: rule_retained_ml_disagreement; rule=overheating; ml=cooling_failure (0.8133). Diagnosis requires review before closing the work order.
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Check cooling airflow and fan operation.
- [ ] Inspect motor surface temperature and thermal hot spots.
- [ ] Verify motor load and duty cycle during the incident.
- [ ] Inspect electrical terminals for loose or heated contacts.
- [ ] Confirm ambient temperature and ventilation conditions.

### LWO-00012 — line1_motor1

- Incident: `INC-0012`
- Priority: **P2**
- Severity: **medium**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T17:16:10` → `2026-05-20T17:20:04`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: medium incident with final diagnosis belt_misalignment; duration 234s; max anomaly 0.5662; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=belt_misalignment (0.9687).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00013 — line1_motor1

- Incident: `INC-0013`
- Priority: **P2**
- Severity: **medium**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T17:20:04` → `2026-05-20T17:23:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: medium incident with final diagnosis belt_misalignment; duration 235s; max anomaly 0.5662; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=belt_misalignment (0.9368).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00014 — line1_motor1

- Incident: `INC-0014`
- Priority: **P2**
- Severity: **medium**
- Fault: **overheating**
- Time window: `2026-05-20T18:27:50` → `2026-05-20T18:32:59`
- Due within: **24 hours**
- Estimated effort: **100 minutes**
- Recommended action: Inspect cooling path, motor load, ambient conditions, and electrical terminals before extended operation.
- Evidence: medium incident with final diagnosis overheating; duration 310s; max anomaly 0.6587; sensors: current_a, temperature_c. Diagnosis source: rule_ml_agreement; rule=overheating; ml=overheating (0.8697).
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Check cooling airflow and fan operation.
- [ ] Inspect motor surface temperature and thermal hot spots.
- [ ] Verify motor load and duty cycle during the incident.
- [ ] Inspect electrical terminals for loose or heated contacts.
- [ ] Confirm ambient temperature and ventilation conditions.

### LWO-00020 — line1_motor1

- Incident: `INC-0020`
- Priority: **P2**
- Severity: **medium**
- Fault: **motor_overload**
- Time window: `2026-05-20T19:29:19` → `2026-05-20T19:33:09`
- Due within: **24 hours**
- Estimated effort: **90 minutes**
- Recommended action: Inspect electrical current draw, mechanical loading, conveyor drag, and drive/VFD overload history.
- Evidence: medium incident with final diagnosis motor_overload; duration 230s; max anomaly 0.6061; sensors: current_a, temperature_c. Diagnosis source: ml_high_confidence_disagreement; rule=overheating; ml=motor_overload (0.872). Diagnosis requires review before closing the work order.
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Inspect motor current draw under production load.
- [ ] Check conveyor for mechanical jam, drag, or overloading.
- [ ] Review drive/VFD overload history and current limits.
- [ ] Verify belt tension and downstream blockage.
- [ ] Reduce load and retest current stability.

### LWO-00021 — line1_motor1

- Incident: `INC-0021`
- Priority: **P2**
- Severity: **medium**
- Fault: **motor_overload**
- Time window: `2026-05-20T19:33:09` → `2026-05-20T19:36:59`
- Due within: **24 hours**
- Estimated effort: **90 minutes**
- Recommended action: Inspect electrical current draw, mechanical loading, conveyor drag, and drive/VFD overload history.
- Evidence: medium incident with final diagnosis motor_overload; duration 230s; max anomaly 0.6061; sensors: current_a, temperature_c. Diagnosis source: ml_high_confidence_disagreement; rule=overheating; ml=motor_overload (0.932). Diagnosis requires review before closing the work order.
- Safety note: Verify electrical and thermal safety before touching motor housing or terminals.

Checklist:
- [ ] Inspect motor current draw under production load.
- [ ] Check conveyor for mechanical jam, drag, or overloading.
- [ ] Review drive/VFD overload history and current limits.
- [ ] Verify belt tension and downstream blockage.
- [ ] Reduce load and retest current stability.

### LWO-00022 — line1_motor1

- Incident: `INC-0022`
- Priority: **P2**
- Severity: **medium**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T19:45:20` → `2026-05-20T19:48:33`
- Due within: **24 hours**
- Estimated effort: **105 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: medium incident with final diagnosis belt_misalignment; duration 193s; max anomaly 0.609; sensors: current_a, throughput_units_min, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=belt_misalignment; ml=belt_misalignment (0.8712).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00023 — line1_motor1

- Incident: `INC-0023`
- Priority: **P2**
- Severity: **medium**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T19:48:33` → `2026-05-20T19:51:46`
- Due within: **24 hours**
- Estimated effort: **105 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: medium incident with final diagnosis belt_misalignment; duration 193s; max anomaly 0.609; sensors: current_a, throughput_units_min, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=belt_misalignment; ml=belt_misalignment (0.948).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00024 — line1_motor1

- Incident: `INC-0024`
- Priority: **P2**
- Severity: **medium**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T19:51:46` → `2026-05-20T19:54:59`
- Due within: **24 hours**
- Estimated effort: **105 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: medium incident with final diagnosis belt_misalignment; duration 193s; max anomaly 0.609; sensors: current_a, throughput_units_min, vibration_mm_s. Diagnosis source: rule_ml_agreement; rule=belt_misalignment; ml=belt_misalignment (0.8616).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00005 — line1_motor1

- Incident: `INC-0005`
- Priority: **P3**
- Severity: **low**
- Fault: **belt_misalignment**
- Time window: `2026-05-20T15:16:16` → `2026-05-20T15:23:59`
- Due within: **72 hours**
- Estimated effort: **85 minutes**
- Recommended action: Inspect belt tracking, tension, pulley alignment, and roller condition before full-speed restart.
- Evidence: low incident with final diagnosis belt_misalignment; duration 464s; max anomaly 0.3894; sensors: current_a, vibration_mm_s. Diagnosis source: ml_override_generic_rule; rule=vibration_anomaly; ml=belt_misalignment (0.9164).
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Inspect belt tracking and pulley alignment.
- [ ] Check belt tension and edge wear.
- [ ] Inspect idlers/rollers for seizure or uneven rotation.
- [ ] Verify conveyor load distribution.
- [ ] Realign belt before restarting at full load.

### LWO-00007 — line1_motor1

- Incident: `INC-0007`
- Priority: **P3**
- Severity: **low**
- Fault: **throughput_anomaly**
- Time window: `2026-05-20T16:10:32` → `2026-05-20T16:11:19`
- Due within: **72 hours**
- Estimated effort: **40 minutes**
- Recommended action: Review sensor evidence and perform general mechanical/electrical inspection.
- Evidence: low incident with final diagnosis throughput_anomaly; duration 48s; max anomaly 0.2903; sensors: throughput_units_min. Diagnosis source: rule_retained_ml_normal; rule=throughput_anomaly; ml=normal (0.99). Diagnosis requires review before closing the work order.
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Review contributing sensor traces.
- [ ] Inspect machine condition near the incident time window.
- [ ] Check for simultaneous load, temperature, and vibration excursions.
- [ ] Escalate to reliability engineer if repeated.

### LWO-00019 — line1_motor1

- Incident: `INC-0019`
- Priority: **P3**
- Severity: **low**
- Fault: **throughput_anomaly**
- Time window: `2026-05-20T19:26:25` → `2026-05-20T19:27:08`
- Due within: **72 hours**
- Estimated effort: **40 minutes**
- Recommended action: Review sensor evidence and perform general mechanical/electrical inspection.
- Evidence: low incident with final diagnosis throughput_anomaly; duration 44s; max anomaly 0.2903; sensors: throughput_units_min. Diagnosis source: rule_retained_ml_normal; rule=throughput_anomaly; ml=normal (0.986). Diagnosis requires review before closing the work order.
- Safety note: Follow standard maintenance safety procedure before inspection.

Checklist:
- [ ] Review contributing sensor traces.
- [ ] Inspect machine condition near the incident time window.
- [ ] Check for simultaneous load, temperature, and vibration excursions.
- [ ] Escalate to reliability engineer if repeated.
