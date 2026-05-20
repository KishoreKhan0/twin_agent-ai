# Incident Report: INC-0001

## Executive summary

Incident `INC-0001` affected machine `line1_motor1` between `2026-05-20T14:37:22` and `2026-05-20T14:56:59`.
The system classified the event as **high** severity with suspected fault **bearing_wear**.
The maximum anomaly score was **0.7526** and the mean anomaly score was **0.3971**.

## Machine health and maintenance status

- Minimum health score in incident window: **27**
- Latest health score in incident window: **67**
- Latest risk level in incident window: **medium**
- Latest maintenance urgency in incident window: **inspect_within_48h**
- Latest row-level maintenance recommendation: Inspect mechanical alignment, bearings, fasteners, and vibration trend.

## Sensor evidence

The queried sensor window contains **1178** rows from `2026-05-20T14:37:22` to `2026-05-20T14:56:59`.

- `current_a` ranged from **8.68** to **15.26** (start **12.18**, end **10.33**, change **-1.85**).
- `temperature_c` ranged from **51.04** to **95.31** (start **69.54**, end **57.0**, change **-12.54**).
- `throughput_units_min` ranged from **49.87** to **158.66** (start **116.06**, end **70.44**, change **-45.62**).
- `vibration_mm_s` ranged from **0.604** to **2.987** (start **1.409**, end **2.139**, change **0.73**).

### Detector evidence

- `current_a`: value range 8.68 to 15.26; max sensor anomaly score 0.95
- `temperature_c`: value range 51.04 to 95.31; max sensor anomaly score 0.95
- `throughput_units_min`: value range 49.87 to 158.66; max sensor anomaly score 0.55
- `vibration_mm_s`: value range 0.63 to 2.99; max sensor anomaly score 0.95

## Retrieved engineering references

1. **Conveyor Maintenance Guide — Bearing Inspection Procedure** `[conveyor_maintenance_guide.md::Bearing Inspection Procedure]`

   ## Bearing Inspection Procedure When vibration and temperature rise together, inspect the bearing housing first. Check for abnormal noise, heat near the housing, lubrication breakdown, damaged seals, and mechanical play. Reduce load before inspection if the machine is in a warning or critical state.

2. **Conveyor Safety Checklist — Before Inspection** `[safety_checklist.md::Before Inspection]`

   ## Before Inspection Before performing physical inspection, ensure the technician follows site safety procedures. Lockout/tagout may be required depending on the inspection type and local operating rules.

3. **Conveyor Maintenance Guide — Maintenance Priority** `[conveyor_maintenance_guide.md::Maintenance Priority]`

   ## Maintenance Priority - Critical: Stop or reduce operation and inspect immediately. - High: Inspect within 24 hours. - Medium: Inspect within 48 hours. - Watch: Continue monitoring and schedule routine inspection.

4. **Conveyor Maintenance Guide — Routine Inspection** `[conveyor_maintenance_guide.md::Routine Inspection]`

   ## Routine Inspection Technicians should inspect belt condition, belt tension, pulley alignment, bearing housing, lubrication condition, motor mounting bolts, and the cooling path around the motor.

5. **Conveyor Safety Checklist — Conveyor Safety Checklist** `[safety_checklist.md::Conveyor Safety Checklist]`

   # Conveyor Safety Checklist

## Recommended technician actions

- Reduce load or stop operation if the machine remains critical.
- Inspect bearing housing for heat, noise, and mechanical play.
- Check lubrication condition and bearing seals.
- Compare vibration and temperature trends before restarting at full load.

## Uncertainty and limitations

- This report describes a suspected fault based on synthetic sensor data, detector output, and retrieved engineering documents.
- The system cannot physically confirm bearing damage, belt misalignment, cooling failure, or electrical overload without technician inspection.
- This is not a certified safety system or production-grade predictive-maintenance system.

## Copilot response policy

  TwinAgent AI response policy:
  1. Separate measured sensor evidence from engineering document guidance.
  2. Cite retrieved knowledge-base sources when using document guidance.
  3. Use 'suspected fault' instead of claiming physical confirmation.
  4. Include uncertainty and missing-information statements.
  5. Do not claim certified safety or production-grade predictive maintenance.
  6. Recommend practical technician actions based on the current evidence.
