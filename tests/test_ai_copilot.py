"""Tests for the optional AI copilot foundation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.agent.ai_context import CopilotContextBuilder
from twinagent.agent.ai_provider import create_llm_provider
from twinagent.agent.memory import CopilotMemory
from twinagent.agent.question_intent import CopilotIntent
from twinagent.agent.tools import TwinAgentTools
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


def test_create_llm_provider_defaults_to_fallback(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("TWINAGENT_AI_ENABLED", "0")

    provider = create_llm_provider()

    assert not provider.is_available()


def test_copilot_memory_round_trip(tmp_path: Path) -> None:
    memory = CopilotMemory(database_path=tmp_path / "copilot_memory.db")

    memory.add_interaction(
        question="incident time?",
        answer="Incident started at ...",
        intent="incident_time",
        provider="deterministic",
        model="rules",
        incident_id="INC-0001",
    )

    rows = memory.recent_interactions(limit=5, incident_id="INC-0001")

    assert len(rows) == 1
    assert rows[0]["question"] == "incident time?"
    assert rows[0]["intent"] == "incident_time"


def test_context_builder_includes_minimal_time_context(tmp_path: Path) -> None:
    tools = _prepare_tools(tmp_path)
    incident = tools.get_incident("INC-0001")
    builder = CopilotContextBuilder(tools=tools)

    package = builder.build(
        question="incident time?",
        incident=incident,
        intent=CopilotIntent.INCIDENT_TIME,
        memory_items=[],
    )

    assert package.intent == CopilotIntent.INCIDENT_TIME
    assert package.context["incident"]["start_time"] == "2026-05-20T14:37:22"
    assert "sensor_window_summary" not in package.context


def test_context_builder_includes_sensor_context_for_evidence(tmp_path: Path) -> None:
    tools = _prepare_tools(tmp_path)
    incident = tools.get_incident("INC-0001")
    builder = CopilotContextBuilder(tools=tools)

    package = builder.build(
        question="what sensor evidence supports this?",
        incident=incident,
        intent=CopilotIntent.SENSOR_EVIDENCE,
        memory_items=[],
    )

    assert package.intent == CopilotIntent.SENSOR_EVIDENCE
    assert "sensor_window_summary" in package.context
    assert package.context["sensor_window_summary"]["rows"] > 0
