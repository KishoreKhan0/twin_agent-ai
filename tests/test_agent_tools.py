"""Tests for TwinAgent AI agent tools and copilot orchestration."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.agent import TwinAgentCopilot, TwinAgentTools
from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepare_agent_files(tmp_path: Path) -> tuple[Path, Path]:
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

    return processed_path, incidents_path


def _tools(tmp_path: Path) -> TwinAgentTools:
    processed_path, incidents_path = _prepare_agent_files(tmp_path)

    return TwinAgentTools(
        processed_data_path=processed_path,
        incidents_path=incidents_path,
        rag_config_path=PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )


def test_agent_tools_can_load_incident(tmp_path: Path) -> None:
    tools = _tools(tmp_path)

    incidents = tools.list_recent_incidents(machine_id="line1_motor1")
    incident = tools.get_incident("INC-0001")

    assert incidents
    assert incident["incident_id"] == "INC-0001"
    assert incident["machine_id"] == "line1_motor1"


def test_agent_tools_summarize_sensor_window(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    incident = tools.get_incident("INC-0001")

    summary = tools.summarize_sensor_window(
        machine_id=incident["machine_id"],
        start_time=incident["start_time"],
        end_time=incident["end_time"],
        contributing_sensors=incident["contributing_sensors"],
    )

    assert summary["rows"] > 0
    assert summary["max_anomaly_score"] > 0
    assert summary["min_health_score"] <= 100
    assert summary["sensor_summary"]


def test_agent_tools_retrieve_knowledge(tmp_path: Path) -> None:
    tools = _tools(tmp_path)

    results = tools.retrieve_knowledge("bearing wear vibration temperature maintenance", top_k=3)

    assert results
    assert all(result.source.endswith(".md") for result in results)
    assert all(result.citation for result in results)


def test_copilot_generates_grounded_incident_answer(tmp_path: Path) -> None:
    processed_path, incidents_path = _prepare_agent_files(tmp_path)
    tools = TwinAgentTools(
        processed_data_path=processed_path,
        incidents_path=incidents_path,
        rag_config_path=PROJECT_ROOT / "configs" / "rag_config.yaml",
        project_root=PROJECT_ROOT,
    )
    copilot = TwinAgentCopilot(tools=tools)

    answer = copilot.answer_incident_question(
        incident_id="INC-0001",
        question="Why did this incident trigger?",
    )

    assert "Incident `INC-0001`" in answer
    assert "Sensor evidence" in answer
    assert "Engineering document guidance" in answer
    assert "Recommended maintenance actions" in answer
    assert "Uncertainty and limits" in answer
    assert ".md::" in answer
