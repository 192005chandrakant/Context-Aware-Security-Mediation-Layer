"""
CASML — Intent Analyzer

Infers the user's original intent from the request context.
"""

from __future__ import annotations

from app.contracts import UserIntent, ToolRequest, SecurityContext


class IntentAnalyzer:
    """Analyzes and infers user intent from the original request.

    Extracts the user's intended action to later verify alignment
    with the proposed tool invocation.
    """

    async def analyze(
        self,
        tool_request: ToolRequest,
        context: SecurityContext,
    ) -> UserIntent:
        """Infer user intent from the request and context.

        Args:
            tool_request: The proposed tool invocation.
            context: Security context including conversation history.

        Returns:
            UserIntent with intent classification and confidence.
        """
        # --- Stub Implementation ---
        # In production, this would use NLU/LLM to parse intent.

        raw_request = tool_request.original_user_request or "No user request provided"
        intent_summary = f"User requested: {raw_request[:200]}"
        confidence = 0.7 if tool_request.original_user_request else 0.3

        return UserIntent(
            intent_summary=intent_summary,
            confidence=confidence,
            extracted_entities={
                "tool_name": tool_request.tool_name,
                "agent": tool_request.requesting_agent,
            },
            intent_category="tool_invocation",
            raw_request=raw_request,
        )
