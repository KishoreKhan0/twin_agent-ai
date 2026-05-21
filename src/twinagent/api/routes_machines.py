"""Machine-related FastAPI routes for TwinAgent AI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from twinagent.api.dependencies import ApiContext


def register_machine_routes(context: ApiContext) -> APIRouter:
    """Create machine routes using a runtime context."""
    router = APIRouter(prefix="/machines", tags=["machines"])

    @router.get("/latest")
    def get_latest_machine_state(
        machine_id: str = Query(default="line1_motor1", description="Machine ID to inspect."),
    ) -> dict:
        """Return the latest persisted state for a machine."""
        try:
            latest = context.repository().get_latest_machine_state(machine_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        return {
            "machine_id": latest["machine_id"],
            "timestamp": latest["timestamp"],
            "machine_state": latest["machine_state"],
            "health_score": latest["health_score"],
            "risk_level": latest["risk_level"],
            "anomaly_score": latest["anomaly_score"],
            "maintenance_urgency": latest["maintenance_urgency"],
            "maintenance_recommendation": latest["maintenance_recommendation"],
        }

    @router.get("/{machine_id}/window")
    def query_machine_window(
        machine_id: str,
        start_time: str = Query(..., description="Inclusive start timestamp."),
        end_time: str = Query(..., description="Inclusive end timestamp."),
        limit: int = Query(default=200, ge=1, le=2000),
    ) -> dict:
        """Return a sensor window from SQLite."""
        try:
            dataframe = context.repository().query_sensor_window(
                machine_id=machine_id,
                start_time=start_time,
                end_time=end_time,
            )
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        limited = dataframe.head(limit)
        return {
            "machine_id": machine_id,
            "rows": int(len(limited)),
            "total_rows_in_window": int(len(dataframe)),
            "data": limited.to_dict(orient="records"),
        }

    return router
