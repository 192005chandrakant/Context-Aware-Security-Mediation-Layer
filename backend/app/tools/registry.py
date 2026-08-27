"""
CASML — Tool Registry

Central registry for all available tools.
Tools must be registered here before they can be invoked.
"""

from __future__ import annotations

from collections.abc import Callable, Awaitable
from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Metadata about a registered tool."""

    name: str = Field(..., description="Fully qualified tool name, e.g. 'email.send'")
    description: str = Field(default="", description="Human-readable description")
    category: str = Field(default="general", description="Tool category")
    sensitivity: str = Field(default="medium", description="Tool sensitivity: low, medium, high")
    parameters_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema of accepted parameters"
    )
    requires_confirmation: bool = Field(default=False)


class ToolRegistry:
    """Singleton registry for all available tools.

    Tools must be registered before they can be executed.
    The executor uses this registry to look up tool handlers.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, Callable[..., Awaitable[Any]]] = {}

    def register(
        self,
        definition: ToolDefinition,
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        """Register a tool with its handler.

        Args:
            definition: Tool metadata.
            handler: Async callable that implements the tool.
        """
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_definition(self, tool_name: str) -> ToolDefinition | None:
        """Look up a tool definition by name."""
        return self._tools.get(tool_name)

    def get_handler(self, tool_name: str) -> Callable[..., Awaitable[Any]] | None:
        """Look up a tool handler by name."""
        return self._handlers.get(tool_name)

    def list_tools(self) -> list[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools

    @property
    def tool_count(self) -> int:
        return len(self._tools)


# Global registry singleton
tool_registry = ToolRegistry()
