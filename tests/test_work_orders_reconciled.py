"""Tests for work orders using reconciled diagnosis."""

from __future__ import annotations

from twinagent.maintenance import build_work_order_queue


def test_work_orders_prefer_final_diagnosis() -> None:
    incidents = [
        {
            "incident_id": "INC-0001",
            "machine_id": "line1_motor1",
            "severity": "medium",
            "suspected_fault": "vibration_anomaly",
            "final_diagnosis": "bearing_wear",
            "final_diagnosis_source": "ml_override_generic_rule",
            "ml_predicted_fault": "bearing_wear",
            "ml_confidence": 0.96,
            "requires_review": False,
            "start_time": "2026-05-20T14:00:00",
            "end_time": "2026-05-20T14:05:00",
            "duration_seconds": 300,
            "max_anomaly_score": 0.7,
            "contributing_sensors": ["vibration_mm_s"],
        }
    ]

    queue = build_work_order_queue(incidents, work_order_prefix="TWO")

    assert queue.total_work_orders == 1
    assert queue.work_orders[0].suspected_fault == "bearing_wear"
    assert "final diagnosis" in queue.work_orders[0].evidence_summary
    assert "rule=vibration_anomaly" in queue.work_orders[0].evidence_summary
