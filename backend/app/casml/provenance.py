"""
CASML — Provenance Analyzer

Determines the origin and trust chain of a tool request.
Identifies whether content has been tainted by external/untrusted sources.
"""

from __future__ import annotations

from app.contracts import ProvenanceRecord, ProvenanceSource, ToolRequest, SecurityContext


class ProvenanceAnalyzer:
    """Analyzes the provenance (origin chain) of a tool request.

    Determines whether the request originated from trusted user input
    or has been influenced by external/untrusted content (e.g., LLM
    hallucinations, injected content from tool outputs).
    """

    async def analyze(
        self,
        tool_request: ToolRequest,
        context: SecurityContext,
    ) -> ProvenanceRecord:
        """Analyze the provenance of a tool request.

        Args:
            tool_request: The proposed tool invocation.
            context: Security context including conversation history.

        Returns:
            ProvenanceRecord with source classification and taint analysis.
        """
        # --- Stub Implementation ---
        # In production, this would trace the request through the
        # conversation history and identify content origins.

        source = ProvenanceSource.USER
        tainted = False
        confidence = 0.8

        # Simple heuristic: if there's no original user request, mark as agent-originated
        if not tool_request.original_user_request:
            source = ProvenanceSource.AGENT
            confidence = 0.5
            tainted = True

        chain = [source.value]
        if context.previous_tool_calls:
            chain.extend(["tool_output"])
            tainted = True

        return ProvenanceRecord(
            request_id=tool_request.id,
            source=source,
            confidence=confidence,
            chain=chain,
            tainted=tainted,
            details={
                "has_user_request": bool(tool_request.original_user_request),
                "previous_tool_calls_count": len(context.previous_tool_calls),
            },
        )
