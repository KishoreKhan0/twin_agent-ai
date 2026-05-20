"""Tests for TwinAgent AI evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.evaluation import (
    EvaluationBenchmark,
    compute_binary_detection_metrics,
    compute_detection_delay,
    compute_fault_classification_summary,
    compute_incident_diagnosis_metrics,
    compute_incident_overlap_score,
)
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _processed_and_incidents():
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    health = HealthScoreCalculator()
    processed = health.add_health_columns(processed)

    advisor = PredictiveMaintenanceAdvisor()
    processed = advisor.add_maintenance_columns(processed)

    with (PROJECT_ROOT / "configs" / "anomaly_config.yaml").open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    incidents = IncidentDetector.from_config(config).detect_incidents(processed)
    return processed, incidents


def test_binary_detection_metrics_are_in_valid_range() -> None:
    processed, _ = _processed_and_incidents()

    metrics = compute_binary_detection_metrics(processed)

    assert metrics["rows"] == 3600
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1_score"] <= 1
    assert metrics["true_positive"] > 0


def test_detection_delay_reports_fault_episodes() -> None:
    processed, _ = _processed_and_incidents()

    delay = compute_detection_delay(processed)

    assert delay["fault_episodes"] >= 1
    assert delay["detected_episodes"] >= 1
    assert delay["mean_detection_delay_seconds"] is not None


def test_incident_overlap_score_is_valid() -> None:
    processed, incidents = _processed_and_incidents()

    overlap = compute_incident_overlap_score(processed, incidents)

    assert overlap["incident_count"] >= 1
    assert 0 <= overlap["incident_overlap_score"] <= 1
    assert overlap["overlap_rows"] > 0


def test_fault_classification_summary_has_confusion_matrix() -> None:
    processed, _ = _processed_and_incidents()

    summary = compute_fault_classification_summary(processed)

    assert summary["evaluated_rows"] > 0
    assert 0 <= summary["row_alignment_accuracy"] <= 1
    assert summary["confusion_matrix"]


def test_incident_diagnosis_metrics_are_meaningful() -> None:
    processed, incidents = _processed_and_incidents()

    diagnosis = compute_incident_diagnosis_metrics(processed, incidents)

    assert diagnosis["evaluated_incidents"] >= 1
    assert 0 <= diagnosis["incident_diagnosis_accuracy"] <= 1
    assert diagnosis["diagnoses"]
    assert "predicted_fault" in diagnosis["diagnoses"][0]
    assert "truth_faults" in diagnosis["diagnoses"][0]


def test_evaluation_benchmark_writes_reports(tmp_path: Path) -> None:
    processed, incidents = _processed_and_incidents()

    processed_path = tmp_path / "sensor_data_with_anomalies.csv"
    incidents_path = tmp_path / "incidents.json"
    json_output = tmp_path / "evaluation_metrics.json"
    markdown_output = tmp_path / "evaluation_report.md"

    processed.to_csv(processed_path, index=False)
    incidents_path.write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    benchmark = EvaluationBenchmark(
        processed_data_path=processed_path,
        incidents_path=incidents_path,
    )

    benchmark.save_json(json_output)
    benchmark.save_markdown(markdown_output)

    assert json_output.exists()
    assert markdown_output.exists()
    markdown = markdown_output.read_text(encoding="utf-8")
    assert "TwinAgent AI Evaluation Report" in markdown
    assert "Incident-level diagnosis" in markdown
