"""Agent/copilot FastAPI routes for TwinAgent AI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from twinagent.api.dependencies import ApiContext


class IncidentQuestionRequest(BaseModel):
    """Request body for incident copilot questions."""

    incident_id: str = Field(default="INC-0001")
    question: str = Field(
        default="Why did this incident trigger and what should the technician inspect first?"
    )


def register_agent_routes(context: ApiContext) -> APIRouter:
    """Create agent routes using a runtime context."""
    router = APIRouter(prefix="/agent", tags=["agent"])

    @router.post("/incident-question")
    def answer_incident_question(request: IncidentQuestionRequest) -> dict:
        """Answer an incident question using the deterministic copilot."""
        try:
            answer = context.copilot().answer_incident_question(
                incident_id=request.incident_id,
                question=request.question,
            )
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except FileNotFoundError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        return {
            "incident_id": request.incident_id,
            "question": request.question,
            "answer": answer,
        }

    return router
