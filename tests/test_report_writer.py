"""Tests for TwinAgent AI incident report generation."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from twinagent.agent import IncidentReportWriter, TwinAgentTools
from twinagent.analytics import (
    AnomalyDetector,
    HealthScoreCalculator,
    IncidentDetector,
    PredictiveMaintenanceAdvisor,
)
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepare_report_tools(tmp_path: Path) -> TwinAgentTools:
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


def test_report_writer_generates_markdown_sections(tmp_path: Path) -> None:
    tools = _prepare_report_tools(tmp_path)
    writer = IncidentReportWriter(tools=tools)

    report = writer.generate_report_markdown("INC-0001")

    assert "# Incident Report: INC-0001" in report
    assert "## Executive summary" in report
    assert "## Sensor evidence" in report
    assert "## Retrieved engineering references" in report
    assert "## Recommended technician actions" in report
    assert "## Uncertainty and limitations" in report


def test_report_writer_includes_citations_and_fault_context(tmp_path: Path) -> None:
    tools = _prepare_report_tools(tmp_path)
    writer = IncidentReportWriter(tools=tools)

    report = writer.generate_report_markdown("INC-0001")

    assert "bearing_wear" in report
    assert ".md::" in report
    assert "suspected fault" in report.lower()


def test_report_writer_writes_file(tmp_path: Path) -> None:
    tools = _prepare_report_tools(tmp_path)
    writer = IncidentReportWriter(tools=tools)

    output_dir = tmp_path / "reports"
    report_path = writer.write_report("INC-0001", output_dir=output_dir)

    assert report_path.exists()
    assert report_path.name == "INC-0001_report.md"
    assert "Incident Report: INC-0001" in report_path.read_text(encoding="utf-8")


def test_report_writer_mentions_limitations(tmp_path: Path) -> None:
    tools = _prepare_report_tools(tmp_path)
    writer = IncidentReportWriter(tools=tools)

    report = writer.generate_report_markdown("INC-0001")

    assert "not a certified safety system" in report
    assert "technician inspection" in report
