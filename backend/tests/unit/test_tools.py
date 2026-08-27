"""
CASML — Tool Registration Tests
"""

from __future__ import annotations

import pytest

from app.tools.registry import ToolDefinition, ToolRegistry


class TestToolRegistry:
    def setup_method(self) -> None:
        """Fresh registry for each test."""
        self.registry = ToolRegistry()

    @pytest.mark.asyncio
    async def test_register_tool(self) -> None:
        """Tools can be registered and looked up."""
        async def handler(**kwargs):
            return {"result": "ok"}

        definition = ToolDefinition(
            name="test.tool",
            description="A test tool",
            category="test",
            sensitivity="low",
        )
        self.registry.register(definition, handler)

        assert self.registry.has_tool("test.tool")
        assert self.registry.tool_count == 1

    def test_get_definition(self) -> None:
        """Tool definition can be retrieved by name."""
        async def handler(**kwargs):
            return {}

        definition = ToolDefinition(name="test.get", description="Get test")
        self.registry.register(definition, handler)

        result = self.registry.get_definition("test.get")
        assert result is not None
        assert result.name == "test.get"

    def test_get_nonexistent_tool(self) -> None:
        """Looking up a nonexistent tool returns None."""
        assert self.registry.get_definition("nonexistent") is None
        assert self.registry.get_handler("nonexistent") is None
        assert not self.registry.has_tool("nonexistent")

    def test_list_tools(self) -> None:
        """List all registered tools."""
        async def handler(**kwargs):
            return {}

        for i in range(3):
            self.registry.register(
                ToolDefinition(name=f"test.tool_{i}"),
                handler,
            )

        tools = self.registry.list_tools()
        assert len(tools) == 3
