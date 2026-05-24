"""End-to-end pipeline orchestration for TwinAgent AI.

The project has multiple production-style scripts:

- bootstrap local data
- train ML model
- predict fault windows
- export ML explainability
- enrich incidents with ML diagnosis
- reconcile rule/ML diagnosis
- generate fleet data
- export fleet analysis and triage
- export work orders

This module makes that workflow reproducible through one backend runner.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


@dataclass(frozen=True)
class PipelineStep:
    """One executable pipeline step."""

    name: str
    command: list[str]
    required_outputs: list[str]
    description: str


@dataclass(frozen=True)
class PipelineConfig:
    """Pipeline execution configuration."""

    project_root: Path
    python_executable: str = sys.executable
    include_tests: bool = False
    include_fleet: bool = True
    stop_on_failure: bool = True
    write_summary: bool = True


@dataclass(frozen=True)
class PipelineStepResult:
    """Result for one executed pipeline step."""

    name: str
    command: list[str]
    return_code: int
    duration_seconds: float
    status: str
    required_outputs: list[str]
    missing_outputs: list[str]
    stdout_tail: str
    stderr_tail: str


@dataclass(frozen=True)
class PipelineRunResult:
    """End-to-end pipeline run result."""

    status: str
    project_root: str
    started_at_epoch: float
    finished_at_epoch: float
    duration_seconds: float
    steps: list[PipelineStepResult]
    artifact_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable result."""
        return {
            "status": self.status,
            "project_root": self.project_root,
            "started_at_epoch": self.started_at_epoch,
            "finished_at_epoch": self.finished_at_epoch,
            "duration_seconds": self.duration_seconds,
            "steps": [asdict(step) for step in self.steps],
            "artifact_summary": self.artifact_summary,
        }


def build_pipeline_steps(config: PipelineConfig) -> list[PipelineStep]:
    """Build the ordered pipeline steps for the configured run."""
    py = config.python_executable
    steps: list[PipelineStep] = []

    if config.include_tests:
        steps.append(
            PipelineStep(
                name="pytest",
                command=[py, "-m", "pytest"],
                required_outputs=[],
                description="Run the full automated test suite before pipeline execution.",
            )
        )

    steps.extend(
        [
            PipelineStep(
                name="bootstrap_local_demo_data",
                command=[py, "scripts/bootstrap_demo_data.py"],
                required_outputs=[
                    "data/generated/sensor_data.csv",
                    "data/processed/sensor_data_with_anomalies.csv",
                    "data/incidents/incidents.json",
                    "data/processed/twinagent.db",
                ],
                description="Generate rich local demo data, local incidents, reports, and SQLite database.",
            ),
            PipelineStep(
                name="train_fault_classifier",
                command=[py, "scripts/train_fault_classifier.py"],
                required_outputs=[
                    "models/fault_classifier.joblib",
                    "models/fault_classifier_metrics.json",
                    "models/fault_classifier_report.md",
                ],
                description="Train the ML fault classifier and export training metrics.",
            ),
            PipelineStep(
                name="predict_fault_windows",
                command=[py, "scripts/predict_faults.py"],
                required_outputs=[
                    "data/processed/sensor_data_with_fault_predictions.csv",
                ],
                description="Run the trained ML classifier over local sensor windows.",
            ),
            PipelineStep(
                name="explain_fault_classifier",
                command=[py, "scripts/explain_fault_classifier.py"],
                required_outputs=[
                    "models/fault_classifier_feature_importance.csv",
                    "models/fault_classifier_error_analysis.json",
                    "models/fault_classifier_model_card.md",
                    "data/processed/fault_prediction_audit.csv",
                ],
                description="Export ML feature importance, error analysis, audit CSV, and model card.",
            ),
            PipelineStep(
                name="enrich_incidents_with_ml",
                command=[py, "scripts/enrich_incidents_with_ml.py"],
                required_outputs=[
                    "data/incidents/incidents_with_ml.json",
                    "data/reports/ml_incident_diagnosis_report.md",
                ],
                description="Attach ML diagnosis, confidence, and agreement metadata to local incidents.",
            ),
            PipelineStep(
                name="reconcile_incident_diagnoses",
                command=[py, "scripts/reconcile_incident_diagnoses.py"],
                required_outputs=[
                    "data/incidents/incidents_reconciled.json",
                    "data/reports/diagnosis_reconciliation_report.md",
                ],
                description="Create final diagnosis fields from rule and ML diagnosis evidence.",
            ),
        ]
    )

    if config.include_fleet:
        steps.extend(
            [
                PipelineStep(
                    name="generate_fleet_demo_data",
                    command=[py, "scripts/generate_fleet_demo_data.py"],
                    required_outputs=[
                        "data/fleet/generated/fleet_sensor_data.csv",
                        "data/fleet/processed/fleet_sensor_data_with_anomalies.csv",
                        "data/fleet/incidents/fleet_incidents.json",
                        "data/fleet/processed/twinagent_fleet.db",
                        "data/fleet/reports/fleet_summary.json",
                        "data/fleet/reports/fleet_summary.md",
                    ],
                    description="Generate expanded fleet sensor data, fleet incidents, SQLite DB, and fleet summary.",
                ),
                PipelineStep(
                    name="export_global_fleet_analysis",
                    command=[py, "scripts/export_global_fleet_analysis.py"],
                    required_outputs=[
                        "data/fleet/reports/global_fleet_analysis.json",
                        "data/fleet/reports/global_fleet_analysis.md",
                    ],
                    description="Export global fleet fault-pattern analysis.",
                ),
                PipelineStep(
                    name="export_fleet_triage",
                    command=[py, "scripts/export_fleet_triage.py"],
                    required_outputs=[
                        "data/fleet/reports/fleet_triage.json",
                        "data/fleet/reports/fleet_triage.md",
                    ],
                    description="Export fleet maintenance priority ranking.",
                ),
            ]
        )

    work_order_command = [
        py,
        "scripts/export_work_orders.py",
        "--local-incidents",
        "data/incidents/incidents_reconciled.json",
    ]
    steps.append(
        PipelineStep(
            name="export_work_orders",
            command=work_order_command,
            required_outputs=[
                "data/reports/local_work_orders.json",
                "data/reports/local_work_orders.md",
                "data/fleet/reports/fleet_work_orders.json",
                "data/fleet/reports/fleet_work_orders.md",
            ]
            if config.include_fleet
            else [
                "data/reports/local_work_orders.json",
                "data/reports/local_work_orders.md",
            ],
            description="Export work orders using reconciled local diagnoses and fleet incidents.",
        )
    )

    return steps


def run_full_pipeline(config: PipelineConfig) -> PipelineRunResult:
    """Run the full TwinAgent AI backend pipeline."""
    started = time.time()
    step_results: list[PipelineStepResult] = []
    status = "passed"

    for step in build_pipeline_steps(config):
        result = _run_step(step=step, project_root=config.project_root)
        step_results.append(result)

        if result.status != "passed":
            status = "failed"
            if config.stop_on_failure:
                break

    finished = time.time()
    artifact_summary = collect_artifact_summary(config.project_root)
    run_result = PipelineRunResult(
        status=status,
        project_root=str(config.project_root),
        started_at_epoch=started,
        finished_at_epoch=finished,
        duration_seconds=round(finished - started, 3),
        steps=step_results,
        artifact_summary=artifact_summary,
    )

    if config.write_summary:
        write_pipeline_summary(config.project_root, run_result)

    return run_result


def validate_required_outputs(project_root: Path, required_outputs: list[str]) -> list[str]:
    """Return missing required outputs relative to project root."""
    missing: list[str] = []
    for relative_path in required_outputs:
        if not (project_root / relative_path).exists():
            missing.append(relative_path)
    return missing


def collect_artifact_summary(project_root: Path) -> dict[str, Any]:
    """Collect compact counts and artifact existence checks after a run."""
    summary: dict[str, Any] = {
        "local": {},
        "fleet": {},
        "ml": {},
        "reports": {},
    }

    local_incidents = _read_json_if_exists(project_root / "data" / "incidents" / "incidents.json")
    reconciled_incidents = _read_json_if_exists(project_root / "data" / "incidents" / "incidents_reconciled.json")
    fleet_summary = _read_json_if_exists(project_root / "data" / "fleet" / "reports" / "fleet_summary.json")
    metrics = _read_json_if_exists(project_root / "models" / "fault_classifier_metrics.json")
    local_work_orders = _read_json_if_exists(project_root / "data" / "reports" / "local_work_orders.json")
    fleet_work_orders = _read_json_if_exists(project_root / "data" / "fleet" / "reports" / "fleet_work_orders.json")

    summary["local"]["incident_count"] = len(local_incidents) if isinstance(local_incidents, list) else 0
    summary["local"]["reconciled_incident_count"] = len(reconciled_incidents) if isinstance(reconciled_incidents, list) else 0

    if isinstance(fleet_summary, dict):
        fleet = fleet_summary.get("fleet", {})
        summary["fleet"]["machine_count"] = int(fleet.get("machine_count", 0))
        summary["fleet"]["incident_count"] = int(fleet.get("incident_rows", 0))
        summary["fleet"]["sensor_rows"] = int(fleet.get("sensor_rows", 0))
    else:
        summary["fleet"]["machine_count"] = 0
        summary["fleet"]["incident_count"] = 0
        summary["fleet"]["sensor_rows"] = 0

    if isinstance(metrics, dict):
        summary["ml"]["window_count"] = int(metrics.get("window_count", 0))
        summary["ml"]["feature_count"] = int(metrics.get("feature_count", 0))
        summary["ml"]["class_count"] = int(metrics.get("class_count", 0))
        summary["ml"]["accuracy"] = metrics.get("accuracy")
        summary["ml"]["macro_f1"] = metrics.get("macro_f1")
        summary["ml"]["weighted_f1"] = metrics.get("weighted_f1")

    if isinstance(local_work_orders, dict):
        summary["reports"]["local_work_orders"] = int(local_work_orders.get("total_work_orders", 0))
    else:
        summary["reports"]["local_work_orders"] = 0

    if isinstance(fleet_work_orders, dict):
        summary["reports"]["fleet_work_orders"] = int(fleet_work_orders.get("total_work_orders", 0))
    else:
        summary["reports"]["fleet_work_orders"] = 0

    summary["reports"]["pipeline_summary_json"] = str(project_root / "data" / "reports" / "pipeline_run_summary.json")
    summary["reports"]["pipeline_summary_md"] = str(project_root / "data" / "reports" / "pipeline_run_summary.md")
    return summary


def write_pipeline_summary(project_root: Path, result: PipelineRunResult) -> None:
    """Write pipeline run summary JSON and Markdown."""
    reports_dir = project_root / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_path = reports_dir / "pipeline_run_summary.json"
    markdown_path = reports_dir / "pipeline_run_summary.md"

    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    markdown_path.write_text(pipeline_result_to_markdown(result), encoding="utf-8")


def pipeline_result_to_markdown(result: PipelineRunResult) -> str:
    """Convert pipeline result to Markdown."""
    lines = [
        "# TwinAgent AI Pipeline Run Summary",
        "",
        "## Status",
        "",
        f"- Status: **{result.status}**",
        f"- Duration: **{result.duration_seconds}s**",
        f"- Project root: `{result.project_root}`",
        "",
        "## Steps",
        "",
        "| Step | Status | Duration | Missing outputs |",
        "|---|---|---:|---|",
    ]

    for step in result.steps:
        missing = ", ".join(step.missing_outputs) if step.missing_outputs else "none"
        lines.append(f"| {step.name} | {step.status} | {step.duration_seconds}s | {missing} |")

    lines.extend(["", "## Artifact summary", ""])
    for group_name, values in result.artifact_summary.items():
        lines.append(f"### {group_name}")
        lines.append("")
        if isinstance(values, dict):
            for key, value in values.items():
                lines.append(f"- {key}: `{value}`")
        else:
            lines.append(f"- `{values}`")
        lines.append("")

    return "\n".join(lines)


def _run_step(*, step: PipelineStep, project_root: Path) -> PipelineStepResult:
    """Execute one pipeline step."""
    started = time.time()
    completed = subprocess.run(
        step.command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    finished = time.time()

    missing = validate_required_outputs(project_root, step.required_outputs)
    status = "passed" if completed.returncode == 0 and not missing else "failed"

    return PipelineStepResult(
        name=step.name,
        command=step.command,
        return_code=int(completed.returncode),
        duration_seconds=round(finished - started, 3),
        status=status,
        required_outputs=step.required_outputs,
        missing_outputs=missing,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


def _tail(text: str, *, max_lines: int = 20) -> str:
    """Return last N lines of text."""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def _read_json_if_exists(path: Path) -> Any:
    """Read JSON if path exists, otherwise return None."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
