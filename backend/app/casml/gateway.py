"""
CASML — Authorization Gateway

Final authorization gate — produces the definitive allow/deny decision.

SECURITY INVARIANT: No tool may execute without passing through this gateway.
"""

from __future__ import annotations

from app.contracts import (
    AuthorizationDecision,
    DecisionAction,
    PolicyDecision,
    RiskResult,
    ToolRequest,
)


class AuthorizationGateway:
    """Final authorization checkpoint before tool execution.

    This is the last gate in the CASML pipeline. Its decision
    determines whether a tool request proceeds to execution.
    """

    async def authorize(
        self,
        tool_request: ToolRequest,
        policy: PolicyDecision,
        risk: RiskResult,
    ) -> AuthorizationDecision:
        """Make the final authorization decision.

        Args:
            tool_request: The proposed tool invocation.
            policy: Policy engine decision.
            risk: Risk assessment result.

        Returns:
            AuthorizationDecision — the definitive gate verdict.
        """
        authorized = policy.action == DecisionAction.ALLOW
        requires_sandbox = policy.action == DecisionAction.SANDBOX

        # If sandboxed, still authorize but in restricted mode
        if requires_sandbox:
            authorized = True

        action = policy.action
        explanation_parts = [
            f"Policy action: {policy.action.value}",
            f"Risk: {risk.risk_level.value} ({risk.risk_score:.2f})",
        ]

        if policy.matched_policies:
            explanation_parts.append(f"Policies: {', '.join(policy.matched_policies)}")

        return AuthorizationDecision(
            request_id=tool_request.id,
            authorized=authorized,
            action=action,
            requires_sandbox=requires_sandbox,
            explanation=" | ".join(explanation_parts),
        )
