"""FastAPI application for TwinAgent AI.

The API serves generated pipeline artifacts and keeps compatibility with the
original local demo endpoints.

Run the pipeline first for full artifact coverage:

    python scripts/run_full_pipeline.py

Then start the API:

    python scripts/launch_api.py

Swagger UI:

    http://localhost:8000/docs
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from twinagent.api.artifacts import (
    artifact_paths,
    artifact_status,
    compact_system_summary,
    project_root_from_api_file,
    read_csv_preview,
    read_json,
    read_latest_sensor_row,
    read_markdown,
)

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


class IncidentQuestionRequest(BaseModel):
    """Request body for incident question endpoint."""

    incident_id: str
    question: str
    copilot_mode: str | None = "deterministic"


def create_app(project_root: str | Path | None = None) -> FastAPI:
    """Create the TwinAgent AI FastAPI app."""
    root = Path(project_root) if project_root is not None else project_root_from_api_file()
    paths = artifact_paths(root)

    app = FastAPI(
        title="TwinAgent AI API",
        description=(
            "Evidence-grounded maintenance intelligence API for the TwinAgent AI "
            "industrial digital twin pipeline."
        ),
        version="0.34.1",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root_endpoint() -> dict[str, Any]:
        """API landing endpoint."""
        return {
            "service": "TwinAgent AI API",
            "tagline": "Evidence-grounded maintenance intelligence",
            "version": "0.34.1",
            "docs": "/docs",
            "health": "/health",
            "artifact_status": "/artifacts/status",
            "legacy_endpoints": [
                "/machines/latest",
                "/machines/{machine_id}/window",
                "/incidents",
                "/agent/incident-question",
            ],
        }

    @app.get("/health")
    def health() -> dict[str, Any]:
        """Health endpoint with legacy and artifact readiness information."""
        status = artifact_status(root)
        local_rows = _local_sensor_rows(paths["local_processed_data"])
        local_incidents = _load_incidents(paths, prefer_reconciled=False)
        latest = read_latest_sensor_row(paths["local_processed_data"])

        return {
            "status": "ok",
            "sensor_rows": local_rows,
            "incident_count": len(local_incidents),
            "incidents_loaded": len(local_incidents),
            "latest_machine_id": latest.get("machine_id"),
            "latest_timestamp": latest.get("timestamp"),
            "artifact_status": status["status"],
            "missing_required": status["missing_required"],
            "summary": compact_system_summary(root),
        }

    @app.get("/artifacts/status")
    def artifacts_status() -> dict[str, Any]:
        """Return metadata for all known generated artifacts."""
        return artifact_status(root)

    @app.get("/summary")
    def summary() -> dict[str, Any]:
        """Return compact system summary."""
        return compact_system_summary(root)

    @app.get("/pipeline/summary")
    def pipeline_summary() -> dict[str, Any]:
        """Return latest full pipeline run summary."""
        return _json_or_404(paths["pipeline_summary"], "Run python scripts/run_full_pipeline.py first.")

    @app.post("/pipeline/run")
    def run_pipeline(
        include_tests: bool = Query(default=False),
        local_only: bool = Query(default=False),
    ) -> dict[str, Any]:
        """Run the backend pipeline from the API.

        This is intended for local demo/dev use. For production systems, prefer
        an external scheduler or CI job.
        """
        command = [sys.executable, "scripts/run_full_pipeline.py"]
        if include_tests:
            command.append("--include-tests")
        if local_only:
            command.append("--local-only")

        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "command": command,
            "return_code": completed.returncode,
            "status": "passed" if completed.returncode == 0 else "failed",
            "stdout_tail": _tail(completed.stdout),
            "stderr_tail": _tail(completed.stderr),
        }

    @app.get("/machine/status")
    def machine_status() -> dict[str, Any]:
        """Return latest local machine status."""
        latest = read_latest_sensor_row(paths["local_processed_data"])
        if not latest:
            raise HTTPException(status_code=404, detail="Processed local data not found.")
        return latest

    @app.get("/machines/latest")
    def latest_machine(
        machine_id: str | None = Query(default=None),
    ) -> dict[str, Any]:
        """Legacy endpoint: return latest reading for one machine."""
        dataframe = _read_processed_dataframe(paths["local_processed_data"])
        if dataframe.empty:
            raise HTTPException(status_code=404, detail="Processed local data not found.")

        if machine_id is not None and "machine_id" in dataframe.columns:
            dataframe = dataframe[dataframe["machine_id"].astype(str) == machine_id]

        if dataframe.empty:
            raise HTTPException(status_code=404, detail=f"No readings found for machine_id={machine_id}")

        dataframe = dataframe.sort_values("timestamp")
        latest = dataframe.iloc[-1].to_dict()
        return _json_safe(latest)

    @app.get("/machines/{machine_id}/window")
    def machine_window(
        machine_id: str,
        start_time: str,
        end_time: str,
        limit: int = Query(default=100, ge=1, le=5000),
    ) -> dict[str, Any]:
        """Legacy endpoint: return readings for a machine within a time window."""
        dataframe = _read_processed_dataframe(paths["local_processed_data"])
        if dataframe.empty:
            raise HTTPException(status_code=404, detail="Processed local data not found.")

        if "machine_id" in dataframe.columns:
            dataframe = dataframe[dataframe["machine_id"].astype(str) == machine_id]

        if dataframe.empty:
            return {
                "machine_id": machine_id,
                "count": 0,
                "rows": 0,
                "readings": [],
            }

        frame = dataframe.copy()
        frame["timestamp_dt"] = _to_datetime(frame["timestamp"])
        start_dt = _parse_time(start_time)
        end_dt = _parse_time(end_time)
        frame = frame[
            (frame["timestamp_dt"] >= start_dt)
            & (frame["timestamp_dt"] <= end_dt)
        ].sort_values("timestamp_dt")

        frame = frame.drop(columns=["timestamp_dt"]).head(limit)

        row_count = int(len(frame))
        return {
            "machine_id": machine_id,
            "start_time": start_time,
            "end_time": end_time,
            "count": row_count,
            "rows": row_count,
            "readings": _records(frame),
        }

    @app.get("/incidents")
    def incidents_alias() -> dict[str, Any]:
        """Legacy endpoint: return local incidents as count + incidents list.

        Newer artifact-focused endpoint remains available at /incidents/local.
        """
        incidents = _load_incidents(paths, prefer_reconciled=False)
        return {
            "count": len(incidents),
            "incidents": incidents,
        }

    @app.get("/incidents/local")
    def local_incidents() -> list[dict[str, Any]]:
        """Return local raw incident records."""
        return _load_incidents(paths, prefer_reconciled=False)

    @app.get("/incidents/reconciled")
    def reconciled_incidents() -> list[dict[str, Any]]:
        """Return local incidents with ML and final reconciled diagnosis fields."""
        return _load_incidents(paths, prefer_reconciled=True)

    @app.get("/incidents/{incident_id}")
    def get_incident(incident_id: str) -> dict[str, Any]:
        """Return one incident by ID, preferring reconciled incidents."""
        for incident in _load_incidents(paths, prefer_reconciled=True):
            if str(incident.get("incident_id")) == incident_id:
                return incident
        raise HTTPException(status_code=404, detail=f"Incident not found: {incident_id}")

    @app.post("/agent/incident-question")
    def answer_incident_question(request: IncidentQuestionRequest) -> dict[str, Any]:
        """Legacy endpoint: answer a question about one incident.

        Uses the project copilot when available, with a deterministic fallback so
        the API stays functional in minimal test fixtures.
        """
        try:
            from twinagent.agent import TwinAgentCopilot

            copilot = TwinAgentCopilot.from_project_root(root)
            try:
                answer = copilot.answer_incident_question(
                    incident_id=request.incident_id,
                    question=request.question,
                    copilot_mode=request.copilot_mode or "deterministic",
                )
            except TypeError:
                answer = copilot.answer_incident_question(
                    incident_id=request.incident_id,
                    question=request.question,
                )
        except Exception:
            incident = None
            for candidate in _load_incidents(paths, prefer_reconciled=True):
                if str(candidate.get("incident_id")) == request.incident_id:
                    incident = candidate
                    break
            if incident is None:
                raise HTTPException(status_code=404, detail=f"Incident not found: {request.incident_id}")
            answer = _fallback_incident_answer(incident, request.question)

        return {
            "incident_id": request.incident_id,
            "question": request.question,
            "answer": answer,
        }

    @app.get("/ml/metrics")
    def ml_metrics() -> dict[str, Any]:
        """Return ML classifier metrics."""
        return _json_or_404(paths["ml_metrics"], "Run python scripts/train_fault_classifier.py first.")

    @app.get("/ml/error-analysis")
    def ml_error_analysis() -> dict[str, Any]:
        """Return ML prediction error analysis."""
        return _json_or_404(paths["ml_error_analysis"], "Run python scripts/explain_fault_classifier.py first.")

    @app.get("/ml/feature-importance")
    def ml_feature_importance(limit: int = Query(default=25, ge=1, le=500)) -> list[dict[str, Any]]:
        """Return ML feature importance rows."""
        return read_csv_preview(paths["ml_feature_importance"], limit=limit)

    @app.get("/ml/model-card")
    def ml_model_card() -> dict[str, Any]:
        """Return ML model card Markdown."""
        text = read_markdown(paths["ml_model_card"], default="")
        if not text:
            raise HTTPException(status_code=404, detail="Model card not found.")
        return {"markdown": text}

    @app.get("/work-orders/local")
    def local_work_orders() -> dict[str, Any]:
        """Return local work orders generated from reconciled incidents."""
        return _json_or_404(paths["local_work_orders"], "Run python scripts/export_work_orders.py first.")

    @app.get("/work-orders/fleet")
    def fleet_work_orders() -> dict[str, Any]:
        """Return fleet work orders."""
        return _json_or_404(paths["fleet_work_orders"], "Run python scripts/export_work_orders.py first.")

    @app.get("/fleet/summary")
    def fleet_summary() -> dict[str, Any]:
        """Return fleet summary."""
        return _json_or_404(paths["fleet_summary"], "Run python scripts/generate_fleet_demo_data.py first.")

    @app.get("/fleet/incidents")
    def fleet_incidents() -> list[dict[str, Any]]:
        """Return fleet incident records."""
        return read_json(paths["fleet_incidents"], default=[]) or []

    @app.get("/fleet/triage")
    def fleet_triage() -> dict[str, Any]:
        """Return fleet triage report."""
        return _json_or_404(paths["fleet_triage"], "Run python scripts/export_fleet_triage.py first.")

    @app.get("/fleet/analysis")
    def fleet_analysis() -> dict[str, Any]:
        """Return global fleet fault-pattern analysis."""
        return _json_or_404(paths["fleet_global_analysis"], "Run python scripts/export_global_fleet_analysis.py first.")

    return app


def _json_or_404(path: Path, message: str) -> Any:
    """Return JSON artifact or raise HTTP 404."""
    payload = read_json(path, default=None)
    if payload is None:
        raise HTTPException(status_code=404, detail=message)
    return payload


def _load_incidents(paths: dict[str, Path], *, prefer_reconciled: bool) -> list[dict[str, Any]]:
    """Load incidents, optionally preferring reconciled records."""
    candidates = (
        [paths["local_incidents_reconciled"], paths["local_incidents"]]
        if prefer_reconciled
        else [paths["local_incidents"]]
    )
    for path in candidates:
        payload = read_json(path, default=None)
        if isinstance(payload, list):
            return payload
    return []


def _read_processed_dataframe(path: Path):
    """Read local processed CSV."""
    if pd is None or not path.exists():
        return _empty_dataframe()
    return pd.read_csv(path)


def _empty_dataframe():
    """Return an empty DataFrame when pandas is available."""
    if pd is None:
        return []
    return pd.DataFrame()


def _local_sensor_rows(path: Path) -> int:
    """Return number of local processed sensor rows."""
    dataframe = _read_processed_dataframe(path)
    return int(len(dataframe)) if hasattr(dataframe, "__len__") else 0


def _parse_time(value: str):
    """Parse timestamp with pandas."""
    if pd is None:
        return value
    return pd.Timestamp(value)


def _to_datetime(series):
    """Convert timestamp series to datetime."""
    if pd is None:
        return series
    return pd.to_datetime(series)


def _records(dataframe) -> list[dict[str, Any]]:
    """Return JSON-safe records from a DataFrame."""
    if pd is None:
        return []
    return [_json_safe(row) for row in dataframe.to_dict(orient="records")]


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy values to JSON-safe Python values."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    if pd is not None and pd.isna(value):
        return None
    return value


def _fallback_incident_answer(incident: dict[str, Any], question: str) -> str:
    """Simple deterministic fallback answer for incident questions."""
    final_diagnosis = incident.get("final_diagnosis") or incident.get("suspected_fault", "unknown")
    severity = incident.get("severity", "unknown")
    start_time = incident.get("start_time", "unknown")
    end_time = incident.get("end_time", "unknown")
    sensors = ", ".join(incident.get("contributing_sensors", [])) or "no listed sensors"

    return (
        f"Incident {incident.get('incident_id')} is classified as {severity}. "
        f"Final diagnosis is {final_diagnosis}. "
        f"The incident window is {start_time} to {end_time}. "
        f"Contributing sensors: {sensors}."
    )


def _tail(text: str, *, max_lines: int = 40) -> str:
    """Return tail of command output."""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


app = create_app()
