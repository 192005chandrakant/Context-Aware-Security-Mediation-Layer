"""
CASML — Security Pipeline Orchestrator

The main pipeline that orchestrates all security analysis modules.

Security Flow:
    ToolRequest + SecurityContext
        → ProvenanceAnalyzer
        → InjectionDetector
        → IntentAnalyzer
        → AlignmentEngine
        → RiskEngine
        → PolicyEngine
        → AuthorizationGateway
        → SecurityDecision
"""

from __future__ import annotations

import time

from app.casml.alignment import AlignmentEngine
from app.casml.detector import InjectionDetector
from app.casml.gateway import AuthorizationGateway
from app.casml.intent import IntentAnalyzer
from app.casml.policy import PolicyEngine
from app.casml.provenance import ProvenanceAnalyzer
from app.casml.risk import RiskEngine
from app.contracts import SecurityContext, SecurityDecision, ToolRequest


class CASMLPipeline:
    """Orchestrates the full CASML security analysis pipeline.

    Each component is independently testable and replaceable.
    The pipeline enforces sequential evaluation to ensure every
    tool request is fully analyzed before authorization.
    """

    def __init__(self) -> None:
        self.provenance_analyzer = ProvenanceAnalyzer()
        self.injection_detector = InjectionDetector()
        self.intent_analyzer = IntentAnalyzer()
        self.alignment_engine = AlignmentEngine()
        self.risk_engine = RiskEngine()
        self.policy_engine = PolicyEngine()
        self.authorization_gateway = AuthorizationGateway()

    async def evaluate(
        self,
        tool_request: ToolRequest,
        context: SecurityContext,
    ) -> SecurityDecision:
        """Run the full CASML security pipeline on a tool request.

        Args:
            tool_request: The proposed tool invocation.
            context: Security context (session, history, metadata).

        Returns:
            SecurityDecision — composite verdict with full analysis trace.
        """
        start_time = time.perf_counter()

        # 1. Provenance Analysis
        provenance = await self.provenance_analyzer.analyze(tool_request, context)

        # 2. Injection Detection
        detection = await self.injection_detector.detect(tool_request, context)

        # 3. Intent Analysis
        intent = await self.intent_analyzer.analyze(tool_request, context)

        # 4. Intent/Action Alignment
        alignment = await self.alignment_engine.check_alignment(tool_request, intent)

        # 5. Risk Scoring
        risk = await self.risk_engine.assess(
            tool_request, provenance, detection, alignment
        )

        # 6. Policy Evaluation
        policy = await self.policy_engine.evaluate(tool_request, risk)

        # 7. Authorization Decision
        authorization = await self.authorization_gateway.authorize(
            tool_request, policy, risk
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return SecurityDecision(
            request_id=tool_request.id,
            tool_name=tool_request.tool_name,
            provenance=provenance,
            detection=detection,
            intent=intent,
            alignment=alignment,
            risk=risk,
            policy=policy,
            authorization=authorization,
            overall_action=authorization.action,
            processing_time_ms=elapsed_ms,
        )
