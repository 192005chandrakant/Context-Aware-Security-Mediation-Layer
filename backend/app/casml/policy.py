"""
CASML — Policy Engine

Evaluates security policies against risk assessment results.
"""

from __future__ import annotations

from app.contracts import (
    DecisionAction,
    PolicyDecision,
    RiskLevel,
    RiskResult,
    ToolRequest,
)


class PolicyEngine:
    """Evaluates configurable security policies.

    Maps risk levels and tool categories to security actions
    based on configurable policy rules.
    """

    # Default policy thresholds — should be loaded from configs/policies.yaml
    DEFAULT_POLICIES: dict[str, dict[str, str | float]] = {
        "critical_risk_deny": {
            "description": "Deny all critical-risk requests",
            "risk_level": "critical",
            "action": "deny",
        },
        "high_risk_sandbox": {
            "description": "Sandbox high-risk requests",
            "risk_level": "high",
            "action": "sandbox",
        },
        "medium_risk_escalate": {
            "description": "Escalate medium-risk requests for review",
            "risk_level": "medium",
            "action": "escalate",
        },
        "low_risk_allow": {
            "description": "Allow low-risk requests",
            "risk_level": "low",
            "action": "allow",
        },
    }

    def __init__(self, policies: dict[str, dict[str, str | float]] | None = None) -> None:
        self.policies = policies or self.DEFAULT_POLICIES

    async def evaluate(
        self,
        tool_request: ToolRequest,
        risk: RiskResult,
    ) -> PolicyDecision:
        """Evaluate policies against the risk assessment.

        Args:
            tool_request: The proposed tool invocation.
            risk: Risk assessment result.

        Returns:
            PolicyDecision with action and matched policy details.
        """
        matched_policies: list[str] = []
        action = DecisionAction.DENY  # Default to deny

        # Match policies based on risk level
        for policy_name, policy in self.policies.items():
            if policy.get("risk_level") == risk.risk_level.value:
                matched_policies.append(policy_name)
                action_str = str(policy.get("action", "deny"))
                try:
                    action = DecisionAction(action_str)
                except ValueError:
                    action = DecisionAction.DENY

        # If no policy matched, default based on risk level
        if not matched_policies:
            action = self._default_action(risk.risk_level)
            matched_policies.append("default_policy")

        return PolicyDecision(
            request_id=tool_request.id,
            action=action,
            matched_policies=matched_policies,
            explanation=f"Risk level '{risk.risk_level.value}' → action '{action.value}'",
        )

    @staticmethod
    def _default_action(risk_level: RiskLevel) -> DecisionAction:
        """Default action mapping for unmatched risk levels."""
        mapping = {
            RiskLevel.CRITICAL: DecisionAction.DENY,
            RiskLevel.HIGH: DecisionAction.SANDBOX,
            RiskLevel.MEDIUM: DecisionAction.ESCALATE,
            RiskLevel.LOW: DecisionAction.ALLOW,
        }
        return mapping.get(risk_level, DecisionAction.DENY)
