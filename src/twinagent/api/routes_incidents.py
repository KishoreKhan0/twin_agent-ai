"""Incident-related FastAPI routes for TwinAgent AI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from twinagent.api.dependencies import ApiContext


def register_incident_routes(context: ApiContext) -> APIRouter:
    """Create incident routes using a runtime context."""
    router = APIRouter(prefix="/incidents", tags=["incidents"])

    @router.get("")
    def list_incidents(
        machine_id: str | None = Query(default=None, description="Optional machine ID filter."),
    ) -> dict:
        """List incidents from SQLite."""
        incidents = context.repository().list_incidents(machine_id=machine_id)
        return {
            "count": len(incidents),
            "incidents": incidents,
        }

    @router.get("/{incident_id}")
    def get_incident(incident_id: str) -> dict:
        """Return one incident by ID."""
        try:
            incident = context.repository().get_incident(incident_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        return incident

    return router
