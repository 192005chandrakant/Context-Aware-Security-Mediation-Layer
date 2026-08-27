"""
CASML — Risk Engine

Computes a composite risk score from pipeline analysis results.
"""

from __future__ import annotations

from app.contracts import (
    AlignmentResult,
    DetectionResult,
    ProvenanceRecord,
    RiskLevel,
    RiskResult,
    ToolRequest,
)


class RiskEngine:
    """Computes composite risk scores from security analysis components.

    Combines provenance, injection detection, alignment scores, and
    tool sensitivity into a single risk assessment.
    """

    # Default weights — should be loaded from configs/risk.yaml in production
    DEFAULT_WEIGHTS: dict[str, float] = {
        "provenance": 0.25,
        "injection": 0.35,
        "alignment": 0.25,
        "tool_sensitivity": 0.15,
    }

    # Tool sensitivity ratings
    TOOL_SENSITIVITY: dict[str, float] = {
        "email.send": 0.7,
        "email.forward": 0.8,
        "email.read": 0.3,
        "document.write": 0.5,
        "document.read": 0.2,
        "database.update": 0.8,
        "database.read": 0.3,
        "web.search": 0.2,
        "file.write": 0.6,
        "file.read": 0.2,
    }

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or self.DEFAULT_WEIGHTS

    async def assess(
        self,
        tool_request: ToolRequest,
        provenance: ProvenanceRecord,
        detection: DetectionResult,
        alignment: AlignmentResult,
    ) -> RiskResult:
        """Compute composite risk score.

        Args:
            tool_request: The proposed tool invocation.
            provenance: Provenance analysis result.
            detection: Injection detection result.
            alignment: Alignment analysis result.

        Returns:
            RiskResult with risk level, score, and breakdown.
        """
        # Component scores (0.0 = safe, 1.0 = maximum risk)
        provenance_risk = 1.0 if provenance.tainted else (1.0 - provenance.confidence)
        injection_risk = detection.confidence if detection.injection_detected else 0.0
        alignment_risk = 1.0 - alignment.alignment_score
        tool_risk = self.TOOL_SENSITIVITY.get(tool_request.tool_name, 0.5)

        component_scores = {
            "provenance": provenance_risk,
            "injection": injection_risk,
            "alignment": alignment_risk,
            "tool_sensitivity": tool_risk,
        }

        # Weighted composite score
        risk_score = sum(
            self.weights[key] * component_scores[key] for key in self.weights
        )
        risk_score = min(max(risk_score, 0.0), 1.0)

        # Classify risk level
        risk_level = self._classify_risk(risk_score)

        explanation_parts = []
        if provenance_risk > 0.5:
            explanation_parts.append(f"Provenance risk: {provenance_risk:.2f}")
        if injection_risk > 0.0:
            explanation_parts.append(f"Injection risk: {injection_risk:.2f}")
        if alignment_risk > 0.5:
            explanation_parts.append(f"Alignment risk: {alignment_risk:.2f}")
        if tool_risk > 0.5:
            explanation_parts.append(f"Tool sensitivity: {tool_risk:.2f}")

        return RiskResult(
            request_id=tool_request.id,
            risk_level=risk_level,
            risk_score=risk_score,
            component_scores=component_scores,
            explanation="; ".join(explanation_parts) if explanation_parts else "Low risk",
        )

    @staticmethod
    def _classify_risk(score: float) -> RiskLevel:
        """Classify a risk score into a risk level."""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
