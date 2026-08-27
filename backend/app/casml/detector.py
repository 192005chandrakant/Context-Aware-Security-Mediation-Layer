"""
CASML — Injection Detector

Detects indirect prompt injection attacks in tool requests.
This is a core security module — handle with care.
"""

from __future__ import annotations

from app.contracts import DetectionResult, ToolRequest, SecurityContext


class InjectionDetector:
    """Detects prompt injection attacks in tool requests.

    Analyzes the content of tool request parameters and context
    for signs of injection attacks (direct and indirect).
    """

    # Known injection indicator patterns (simple heuristics for stub)
    INJECTION_INDICATORS: list[str] = [
        "ignore previous instructions",
        "disregard above",
        "system prompt",
        "you are now",
        "forget everything",
        "override",
        "act as",
        "jailbreak",
        "bypass security",
        "ignore all rules",
    ]

    async def detect(
        self,
        tool_request: ToolRequest,
        context: SecurityContext,
    ) -> DetectionResult:
        """Detect injection attacks in a tool request.

        Args:
            tool_request: The proposed tool invocation.
            context: Security context including conversation history.

        Returns:
            DetectionResult with injection classification and confidence.
        """
        # --- Stub Implementation ---
        # In production, this would use ML models (sentence-transformers,
        # fine-tuned classifiers) for detection.

        indicators_found: list[str] = []
        content_to_check = self._extract_content(tool_request)

        for indicator in self.INJECTION_INDICATORS:
            if indicator.lower() in content_to_check.lower():
                indicators_found.append(indicator)

        injection_detected = len(indicators_found) > 0
        confidence = min(len(indicators_found) * 0.3, 1.0) if injection_detected else 0.0

        return DetectionResult(
            request_id=tool_request.id,
            injection_detected=injection_detected,
            injection_type="keyword_heuristic" if injection_detected else None,
            confidence=confidence,
            indicators=indicators_found,
            model_scores={"heuristic": confidence},
            details={
                "content_length": len(content_to_check),
                "indicators_checked": len(self.INJECTION_INDICATORS),
            },
        )

    def _extract_content(self, tool_request: ToolRequest) -> str:
        """Extract all textual content from a tool request for analysis."""
        parts = [
            tool_request.original_user_request,
            str(tool_request.parameters),
        ]
        # Include any string values from context_data
        for value in tool_request.context_data.values():
            if isinstance(value, str):
                parts.append(value)
        return " ".join(parts)
