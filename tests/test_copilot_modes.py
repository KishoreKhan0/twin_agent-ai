"""Tests for selectable TwinAgent copilot modes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from twinagent.agent import TwinAgentCopilot, TwinAgentTools
from twinagent.agent.copilot_mode import CopilotMode, normalize_copilot_mode
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


def test_normalize_copilot_mode_aliases() -> None:
    assert normalize_copilot_mode("deterministic") == CopilotMode.DETERMINISTIC
    assert normalize_copilot_mode("local") == CopilotMode.DETERMINISTIC
    assert normalize_copilot_mode("openai") == CopilotMode.AI
    assert normalize_copilot_mode("auto") == CopilotMode.AUTO


def test_normalize_copilot_mode_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        normalize_copilot_mode("magic")


def test_deterministic_mode_returns_local_answer(tmp_path: Path) -> None:
    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question(
        "INC-0001",
        "incident time?",
        copilot_mode="deterministic",
    )

    assert "started at" in answer
    assert "ended at" in answer


def test_ai_mode_without_provider_falls_back_cleanly(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("TWINAGENT_AI_ENABLED", "0")

    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question(
        "INC-0001",
        "tell me something about the incident",
        copilot_mode="ai",
    )

    assert "INC-0001" in answer
    assert "AI mode was selected" in answer
    assert "RateLimitError" not in answer
    assert "RetryError" not in answer


def test_auto_mode_without_provider_returns_clean_answer(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("TWINAGENT_AI_ENABLED", "0")

    copilot = TwinAgentCopilot(tools=_prepare_tools(tmp_path))

    answer = copilot.answer_incident_question(
        "INC-0001",
        "tell me something about the incident",
        copilot_mode="auto",
    )

    assert "INC-0001" in answer
    assert "AI mode was selected" not in answer
    assert "RateLimitError" not in answer
