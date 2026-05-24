# Diagnosis Reconciliation Engine

Step 32 creates one final diagnosis field from rule and ML diagnoses.

## Why this exists

After Step 31, incidents contain both:

```text
suspected_fault
ml_predicted_fault
```

That is useful, but downstream systems need one technician-facing decision.

This step adds:

```json
{
  "final_diagnosis": "bearing_wear",
  "final_diagnosis_source": "ml_override_generic_rule",
  "diagnosis_confidence": "high",
  "requires_review": false,
  "diagnosis_reason": "Rule label was generic; ML predicted an actionable fault..."
}
```

## Policy examples

### Rule and ML agree

Use the agreed diagnosis.

### Rule is generic, ML is confident and actionable

Use ML.

Example:

```text
rule = vibration_anomaly
ml = bearing_wear
final = bearing_wear
```

### ML says normal, rule says anomaly

Keep rule diagnosis and require review.

### Strong disagreement

Use ML only if confidence and matched-window support are strong; otherwise keep rule and require review.

## Commands

```cmd
python scripts\reconcile_incident_diagnoses.py
```

## Outputs

```text
data/incidents/incidents_reconciled.json
data/reports/diagnosis_reconciliation_report.md
```

## Work-order integration

`work_orders.py` now prefers `final_diagnosis` when present.
