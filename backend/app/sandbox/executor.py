"""
CASML — Sandbox Executor

Provides isolated execution environment for sandboxed tool requests.
"""

from __future__ import annotations

import time
from typing import Any

from app.contracts import ToolRequest, ToolResponse
from app.tools.registry import tool_registry


class Sandbox:
    """Sandboxed execution environment for tools.

    Tools running in the sandbox have restricted capabilities
    and their outputs are marked as sandboxed in the response.
    """

    async def execute(
        self,
        tool_request: ToolRequest,
    ) -> ToolResponse:
        """Execute a tool in sandboxed mode.

        Args:
            tool_request: The approved tool invocation request.

        Returns:
            ToolResponse with sandboxed=True flag.
        """
        handler = tool_registry.get_handler(tool_request.tool_name)
        if handler is None:
            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=False,
                error=f"Tool '{tool_request.tool_name}' not found",
                sandboxed=True,
            )

        start = time.perf_counter()
        try:
            # In production, this would apply resource limits,
            # network isolation, and output filtering
            result = await handler(**tool_request.parameters)
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Sanitize output in sandbox mode
            sanitized = self._sanitize_output(result)

            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=True,
                result=sanitized,
                execution_time_ms=elapsed_ms,
                sandboxed=True,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return ToolResponse(
                request_id=tool_request.id,
                tool_name=tool_request.tool_name,
                success=False,
                error=f"Sandbox execution error: {e}",
                execution_time_ms=elapsed_ms,
                sandboxed=True,
            )

    def _sanitize_output(self, output: Any) -> Any:
        """Sanitize tool output in sandbox mode.

        Redacts potentially sensitive information from tool outputs.
        """
        if isinstance(output, dict):
            return {k: self._sanitize_output(v) for k, v in output.items()}
        elif isinstance(output, list):
            return [self._sanitize_output(item) for item in output]
        elif isinstance(output, str):
            # Redact known fake secret patterns
            for pattern in ["FAKE_API_KEY", "FAKE_PASSWORD", "FAKE_SECRET"]:
                if pattern in output:
                    output = output.replace(output, "[REDACTED]")
            return output
        return output
