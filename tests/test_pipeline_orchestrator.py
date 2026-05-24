"""Tests for TwinAgent AI pipeline orchestration."""

from __future__ import annotations

from pathlib import Path

from twinagent.pipeline import (
    PipelineConfig,
    PipelineRunResult,
    PipelineStepResult,
    build_pipeline_steps,
    validate_required_outputs,
)
from twinagent.pipeline.orchestrator import pipeline_result_to_markdown


def test_build_pipeline_steps_contains_reconciled_work_order_export(tmp_path: Path) -> None:
    config = PipelineConfig(
        project_root=tmp_path,
        python_executable="python",
        include_tests=False,
        include_fleet=True,
    )

    steps = build_pipeline_steps(config)
    names = [step.name for step in steps]

    assert "bootstrap_local_demo_data" in names
    assert "train_fault_classifier" in names
    assert "reconcile_incident_diagnoses" in names
    assert "export_work_orders" in names

    work_order_step = next(step for step in steps if step.name == "export_work_orders")
    assert "data/incidents/incidents_reconciled.json" in work_order_step.command
    assert "data/reports/local_work_orders.json" in work_order_step.required_outputs
    assert "data/fleet/reports/fleet_work_orders.json" in work_order_step.required_outputs


def test_build_pipeline_steps_local_only_skips_fleet(tmp_path: Path) -> None:
    config = PipelineConfig(
        project_root=tmp_path,
        python_executable="python",
        include_tests=False,
        include_fleet=False,
    )

    names = [step.name for step in build_pipeline_steps(config)]

    assert "generate_fleet_demo_data" not in names
    assert "export_fleet_triage" not in names


def test_validate_required_outputs_detects_missing_files(tmp_path: Path) -> None:
    existing = tmp_path / "data" / "reports"
    existing.mkdir(parents=True)
    (existing / "report.md").write_text("ok", encoding="utf-8")

    missing = validate_required_outputs(
        tmp_path,
        [
            "data/reports/report.md",
            "data/reports/missing.md",
        ],
    )

    assert missing == ["data/reports/missing.md"]


def test_pipeline_result_to_markdown_contains_status(tmp_path: Path) -> None:
    result = PipelineRunResult(
        status="passed",
        project_root=str(tmp_path),
        started_at_epoch=1.0,
        finished_at_epoch=2.0,
        duration_seconds=1.0,
        steps=[
            PipelineStepResult(
                name="demo",
                command=["python", "demo.py"],
                return_code=0,
                duration_seconds=0.1,
                status="passed",
                required_outputs=[],
                missing_outputs=[],
                stdout_tail="ok",
                stderr_tail="",
            )
        ],
        artifact_summary={"local": {"incident_count": 24}},
    )

    markdown = pipeline_result_to_markdown(result)

    assert "TwinAgent AI Pipeline Run Summary" in markdown
    assert "demo" in markdown
    assert "passed" in markdown
