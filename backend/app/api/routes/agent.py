"""
CASML — Agent Routes

Endpoints for running the LLM agent with CASML protection.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.casml.pipeline import CASMLPipeline
from app.contracts import SecurityContext, SecurityDecision, ToolRequest

router = APIRouter(prefix="/api/agent", tags=["agent"])

pipeline = CASMLPipeline()


class AgentRunRequest(BaseModel):
    """Request body for running an agent task."""

    user_request: str = Field(..., description="The user's natural language request")
    agent_id: str = Field(default="default_agent")
    session_id: str = Field(default="")
    context: dict = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    """Response from an agent run."""

    request_id: str
    user_request: str
    proposed_tool: str | None = None
    security_decision: SecurityDecision | None = None
    tool_result: dict | None = None
    status: str = "completed"


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    """Run an agent task with CASML protection.

    The agent processes the user request, proposes a tool call,
    and the tool call is analyzed by the CASML pipeline before execution.
    """
    # --- Mock: simulate agent proposing a tool call ---
    tool_request = ToolRequest(
        tool_name="email.read",
        parameters={"mailbox": "inbox", "limit": 5},
        requesting_agent=request.agent_id,
        original_user_request=request.user_request,
    )

    context = SecurityContext(
        session_id=request.session_id or "mock-session",
        user_id="mock-user",
    )

    # Run through CASML pipeline
    decision = await pipeline.evaluate(tool_request, context)

    return AgentRunResponse(
        request_id=tool_request.id,
        user_request=request.user_request,
        proposed_tool=tool_request.tool_name,
        security_decision=decision,
        tool_result={"mock": True, "message": "Agent run completed"},
        status="completed",
    )
