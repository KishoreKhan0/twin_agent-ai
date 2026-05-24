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
    copilot_mode: str = Field(
        default="auto",
        description="Copilot mode: deterministic, ai, or auto.",
    )
    include_metadata: bool = Field(
        default=True,
        description="Return intent, provider, and suggested follow-up metadata.",
    )


def register_agent_routes(context: ApiContext) -> APIRouter:
    """Create agent routes using a runtime context."""
    router = APIRouter(prefix="/agent", tags=["agent"])

    @router.post("/incident-question")
    def answer_incident_question(request: IncidentQuestionRequest) -> dict:
        """Answer an incident question using the selected copilot mode."""
        try:
            copilot = context.copilot()

            if request.include_metadata and hasattr(copilot, "answer_incident_question_with_metadata"):
                result = copilot.answer_incident_question_with_metadata(
                    incident_id=request.incident_id,
                    question=request.question,
                    copilot_mode=request.copilot_mode,
                )
                return result.to_dict()

            answer = copilot.answer_incident_question(
                incident_id=request.incident_id,
                question=request.question,
                copilot_mode=request.copilot_mode,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except FileNotFoundError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

        return {
            "incident_id": request.incident_id,
            "question": request.question,
            "copilot_mode": request.copilot_mode,
            "answer": answer,
        }

    return router
