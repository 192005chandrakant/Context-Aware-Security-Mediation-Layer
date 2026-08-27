"""
CASML — Security Routes

Endpoints for direct security analysis through the CASML pipeline.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.casml.pipeline import CASMLPipeline
from app.contracts import SecurityContext, SecurityDecision, ToolRequest

router = APIRouter(prefix="/api/security", tags=["security"])

pipeline = CASMLPipeline()


class SecurityAnalyzeRequest(BaseModel):
    """Request body for security analysis."""

    tool_name: str = Field(..., description="Tool to analyze")
    parameters: dict = Field(default_factory=dict)
    user_request: str = Field(default="", description="Original user request")
    agent_id: str = Field(default="default_agent")
    session_id: str = Field(default="")
    context_data: dict = Field(default_factory=dict)


@router.post("/analyze", response_model=SecurityDecision)
async def analyze_request(request: SecurityAnalyzeRequest) -> SecurityDecision:
    """Analyze a tool request through the CASML security pipeline.

    Returns the full SecurityDecision with all component analyses.
    """
    tool_request = ToolRequest(
        tool_name=request.tool_name,
        parameters=request.parameters,
        requesting_agent=request.agent_id,
        original_user_request=request.user_request,
        context_data=request.context_data,
    )

    context = SecurityContext(
        session_id=request.session_id or "direct-analysis",
        user_id="analyst",
    )

    decision = await pipeline.evaluate(tool_request, context)
    return decision
