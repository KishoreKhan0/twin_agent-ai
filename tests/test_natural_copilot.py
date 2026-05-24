"""Tests for natural-language copilot improvements."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.agent import TwinAgentCopilot, TwinAgentTools
from twinagent.agent.question_intent import CopilotIntent, classify_copilot_question
from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepare_tools(tmp_path: Path) -> TwinAgentTools:
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

    processed_path = tmp_path / "sensor_data_with_anomalies.csv"
    incidents_path = tmp_path / "incidents.json"

    processed.to_csv(processed_path, index=False)
    incidents_path.write_text(json.dumps(incidents, indent=2), encoding="utf-8")

    return TwinAgentTools(
        processed_data_path=processed_path,
        incidents_path=incidents_path,
        rag_config_path=PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )


def test_messy_question_time_intent() -> None:
    result = classify_copilot_question("issue when?")

    assert result.intent == CopilotIntent.INCIDENT_TIME


def test_messy_question_summary_intent() -> None:
    result = classify_copilot_question("wat happend bro")

    assert result.intent == CopilotIntent.INCIDENT_SUMMARY


def test_messy_question_fault_intent() -> None:
    result = classify_copilot_question("what wrong with motor")

    assert result.intent == CopilotIntent.MACHINE_FAULT


def test_messy_question_severity_intent() -> None:
    result = classify_copilot_question("is it bad?")

    assert result.intent == CopilotIntent.SEVERITY


def test_messy_question_action_intent() -> None:
    result = classify_copilot_question("what should i do now?")

    assert result.intent == CopilotIntent.MAINTENANCE_ACTION


def test_copilot_metadata_contains_intent_and_followups(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    result = copilot.answer_incident_question_with_metadata(
        incident_id="INC-0001",
        question="issue when?",
        copilot_mode="deterministic",
    )

    assert "started at" in result.answer
    assert result.intent == "incident_time"
    assert result.copilot_mode == "deterministic"
    assert result.provider == "deterministic"
    assert result.suggested_followups


def test_copilot_messy_action_question(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    result = copilot.answer_incident_question_with_metadata(
        incident_id="INC-0001",
        question="what should i do now?",
        copilot_mode="deterministic",
    )

    assert "Recommended technician actions" in result.answer
    assert result.intent == "maintenance_action"
