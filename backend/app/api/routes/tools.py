"""
CASML — Tool Routes

Endpoints for tool management and execution.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.casml.pipeline import CASMLPipeline
from app.contracts import SecurityContext, ToolResponse
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolDefinition, tool_registry
from app.contracts import ToolRequest

router = APIRouter(prefix="/api/tools", tags=["tools"])

pipeline = CASMLPipeline()
executor = ToolExecutor()


class ToolExecuteRequest(BaseModel):
    """Request body for tool execution."""

    tool_name: str = Field(..., description="Tool to execute")
    parameters: dict = Field(default_factory=dict)
    user_request: str = Field(default="", description="Original user request")
    agent_id: str = Field(default="default_agent")


@router.get("", response_model=list[ToolDefinition])
async def list_tools() -> list[ToolDefinition]:
    """List all registered tools."""
    return tool_registry.list_tools()


@router.post("/request", response_model=ToolResponse)
async def request_tool_execution(request: ToolExecuteRequest) -> ToolResponse:
    """Submit a tool execution request.

    The request is first analyzed by the CASML pipeline.
    Execution only proceeds if the security decision allows it.
    """
    tool_request = ToolRequest(
        tool_name=request.tool_name,
        parameters=request.parameters,
        requesting_agent=request.agent_id,
        original_user_request=request.user_request,
    )

    context = SecurityContext(user_id="api-user")

    # Run security analysis
    decision = await pipeline.evaluate(tool_request, context)

    # Execute only if authorized
    try:
        response = await executor.execute(tool_request, decision)
    except Exception as e:
        response = ToolResponse(
            request_id=tool_request.id,
            tool_name=tool_request.tool_name,
            success=False,
            error=str(e),
        )

    return response
