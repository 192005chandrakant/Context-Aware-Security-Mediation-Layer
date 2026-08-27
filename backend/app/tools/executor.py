"""
CASML — Tool Executor

Executes tools ONLY when an approved SecurityDecision is present.

SECURITY INVARIANT:
    ToolRequest without approved SecurityDecision → REJECT → Tool NOT executed

This is a critical security boundary. Do not bypass.
"""

from __future__ import annotations

import time

from app.contracts import (
    AuthorizationDecision,
    DecisionAction,
    SecurityDecision,
    ToolRequest,
    ToolResponse,
)
from app.tools.registry import tool_registry


class ToolExecutionError(Exception):
    """Raised when tool execution is denied or fails."""

    pass


class ToolExecutor:
    """Executes tool requests after authorization verification.

    CRITICAL: This executor MUST verify that a valid, approved
    SecurityDecision exists before executing any tool.
    """

    async def execute(
        self,
        tool_request: ToolRequest,
        security_decision: SecurityDecision | None = None,
    ) -> ToolResponse:
        """Execute a tool request if authorized.

        Args:
            tool_request: The tool invocation request.
            security_decision: The CASML security decision. MUST be provided and approved.

        Returns:
            ToolResponse with execution results.

        Raises:
            ToolExecutionError: If authorization is missing or denied.
        """
        # ── SECURITY GATE ─────────────────────────────────
        # This is the critical enforcement point.
        self._verify_authorization(tool_request, security_decision)

        # ── Look up handler ───────────────────────────────
        handler = tool_registry.get_handler(tool_request.tool_name)
        if handler is None:
            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=False,
                error=f"Tool '{tool_request.tool_name}' not found in registry",
            )

        # ── Execute ───────────────────────────────────────
        start = time.perf_counter()
        try:
            result = await handler(**tool_request.parameters)
            elapsed_ms = (time.perf_counter() - start) * 1000

            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=True,
                result=result,
                execution_time_ms=elapsed_ms,
                sandboxed=security_decision.authorization.requires_sandbox
                if security_decision
                else False,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=False,
                error=str(e),
                execution_time_ms=elapsed_ms,
            )

    def _verify_authorization(
        self,
        tool_request: ToolRequest,
        security_decision: SecurityDecision | None,
    ) -> None:
        """Verify that the security decision authorizes execution.

        Raises:
            ToolExecutionError: If authorization is missing, denied, or invalid.
        """
        # No security decision provided at all
        if security_decision is None:
            raise ToolExecutionError(
                f"SECURITY VIOLATION: Tool '{tool_request.tool_name}' execution "
                f"rejected — no SecurityDecision provided. "
                f"All tool executions MUST pass through CASML."
            )

        # Request ID mismatch
        if security_decision.request_id != tool_request.id:
            raise ToolExecutionError(
                f"SECURITY VIOLATION: SecurityDecision request_id "
                f"'{security_decision.request_id}' does not match "
                f"ToolRequest id '{tool_request.id}'."
            )

        # Not authorized
        if not security_decision.authorization.authorized:
            raise ToolExecutionError(
                f"SECURITY VIOLATION: Tool '{tool_request.tool_name}' execution "
                f"denied by authorization gateway. "
                f"Action: {security_decision.authorization.action.value}. "
                f"Reason: {security_decision.authorization.explanation}"
            )

        # Overall action is DENY
        if security_decision.overall_action == DecisionAction.DENY:
            raise ToolExecutionError(
                f"SECURITY VIOLATION: Tool '{tool_request.tool_name}' execution "
                f"denied by CASML pipeline. "
                f"Overall action: {security_decision.overall_action.value}."
            )
