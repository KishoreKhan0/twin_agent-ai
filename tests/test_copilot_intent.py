"""Tests for intent-aware TwinAgent AI copilot answers."""

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


def test_question_intent_detects_time_question() -> None:
    result = classify_copilot_question("Give me the time of the incident")

    assert result.intent == CopilotIntent.INCIDENT_TIME


def test_question_intent_detects_irrelevant_question() -> None:
    result = classify_copilot_question("What is the weather in Berlin?")

    assert result.intent == CopilotIntent.IRRELEVANT


def test_copilot_time_question_is_short(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question("INC-0001", "Give me the time of the incident")

    assert "started at" in answer
    assert "ended at" in answer
    assert "Sensor evidence" not in answer
    assert "Engineering document guidance" not in answer


def test_copilot_fault_question_is_focused(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question("INC-0001", "Which machine fault happened?")

    assert "bearing_wear" in answer
    assert "line1_motor1" in answer
    assert "Engineering document guidance" not in answer


def test_copilot_irrelevant_question_returns_no_result(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question("INC-0001", "What is the weather in Berlin?")

    assert "No relevant incident result" in answer
    assert "bearing_wear" not in answer


def test_copilot_full_report_only_when_requested(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question("INC-0001", "Give me the full report")

    assert "TwinAgent AI Copilot Answer" in answer
    assert "Sensor evidence" in answer
    assert "Engineering document guidance" in answer


def test_copilot_current_status_question(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question("INC-0001", "What is the current machine status?")

    assert "Latest machine status" in answer
    assert "line1_motor1" in answer
    assert "health score" in answer
