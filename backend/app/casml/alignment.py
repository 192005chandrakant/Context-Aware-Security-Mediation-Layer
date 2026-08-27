"""
CASML — Alignment Engine

Verifies that the proposed tool action aligns with the inferred user intent.
"""

from __future__ import annotations

from app.contracts import AlignmentResult, ToolRequest, UserIntent


class AlignmentEngine:
    """Checks alignment between user intent and proposed tool action.

    Detects cases where the agent proposes actions that deviate from
    or contradict the user's original request.
    """

    async def check_alignment(
        self,
        tool_request: ToolRequest,
        user_intent: UserIntent,
    ) -> AlignmentResult:
        """Verify alignment between intent and proposed action.

        Args:
            tool_request: The proposed tool invocation.
            user_intent: The inferred user intent.

        Returns:
            AlignmentResult with alignment score and analysis.
        """
        # --- Stub Implementation ---
        # In production, this would use semantic similarity, LLM-based
        # reasoning, or learned alignment classifiers.

        proposed_action = f"{tool_request.tool_name}({tool_request.parameters})"
        alignment_score = user_intent.confidence  # Simple proxy for now

        # Heuristic: if intent confidence is low, alignment is questionable
        aligned = alignment_score >= 0.5
        misalignment_reasons = []

        if not aligned:
            misalignment_reasons.append(
                "Low intent confidence — cannot verify alignment"
            )

        if not tool_request.original_user_request:
            misalignment_reasons.append(
                "No original user request to align against"
            )
            alignment_score = max(alignment_score - 0.2, 0.0)
            aligned = False

        return AlignmentResult(
            request_id=tool_request.id,
            aligned=aligned,
            alignment_score=alignment_score,
            user_intent=user_intent.intent_summary,
            proposed_action=proposed_action,
            misalignment_reasons=misalignment_reasons,
            details={
                "intent_confidence": user_intent.confidence,
                "intent_category": user_intent.intent_category,
            },
        )
