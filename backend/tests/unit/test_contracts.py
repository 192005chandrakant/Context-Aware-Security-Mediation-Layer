"""
CASML — Contract Validation Tests

Ensure all Pydantic contracts can be instantiated and serialized correctly.
"""

from __future__ import annotations

import pytest

from app.contracts import (
    AlignmentResult,
    AuditEvent,
    AuditEventType,
    AuthorizationDecision,
    DecisionAction,
    DetectionResult,
    ExperimentConfig,
    ExperimentResult,
    PolicyDecision,
    ProvenanceRecord,
    ProvenanceSource,
    RiskLevel,
    RiskResult,
    SecurityContext,
    SecurityDecision,
    ToolRequest,
    ToolResponse,
    UserIntent,
)


class TestToolRequest:
    def test_create_tool_request(self) -> None:
        req = ToolRequest(
            tool_name="email.send",
            parameters={"to": "test@example.com", "subject": "Hello"},
            original_user_request="Send an email to test",
        )
        assert req.tool_name == "email.send"
        assert req.id  # Auto-generated UUID
        assert req.parameters["to"] == "test@example.com"

    def test_tool_request_serialization(self) -> None:
        req = ToolRequest(tool_name="web.search", parameters={"query": "test"})
        data = req.model_dump()
        assert "id" in data
        assert data["tool_name"] == "web.search"

        # Round-trip
        req2 = ToolRequest.model_validate(data)
        assert req2.tool_name == req.tool_name


class TestToolResponse:
    def test_create_tool_response(self) -> None:
        resp = ToolResponse(
            request_id="req-001",
            tool_name="email.read",
            success=True,
            result={"emails": []},
        )
        assert resp.success is True
        assert resp.request_id == "req-001"


class TestSecurityContracts:
    def test_provenance_record(self) -> None:
        record = ProvenanceRecord(
            request_id="req-001",
            source=ProvenanceSource.USER,
            confidence=0.9,
            chain=["user", "agent"],
            tainted=False,
        )
        assert record.source == ProvenanceSource.USER
        assert record.confidence == 0.9

    def test_detection_result(self) -> None:
        result = DetectionResult(
            request_id="req-001",
            injection_detected=True,
            injection_type="keyword_heuristic",
            confidence=0.8,
            indicators=["ignore previous instructions"],
        )
        assert result.injection_detected is True
        assert len(result.indicators) == 1

    def test_user_intent(self) -> None:
        intent = UserIntent(
            intent_summary="User wants to read emails",
            confidence=0.9,
        )
        assert intent.confidence == 0.9

    def test_alignment_result(self) -> None:
        result = AlignmentResult(
            request_id="req-001",
            aligned=True,
            alignment_score=0.85,
        )
        assert result.aligned is True

    def test_risk_result(self) -> None:
        result = RiskResult(
            request_id="req-001",
            risk_level=RiskLevel.LOW,
            risk_score=0.15,
        )
        assert result.risk_level == RiskLevel.LOW

    def test_policy_decision(self) -> None:
        decision = PolicyDecision(
            request_id="req-001",
            action=DecisionAction.ALLOW,
            matched_policies=["low_risk_allow"],
        )
        assert decision.action == DecisionAction.ALLOW

    def test_authorization_decision(self) -> None:
        decision = AuthorizationDecision(
            request_id="req-001",
            authorized=True,
            action=DecisionAction.ALLOW,
        )
        assert decision.authorized is True

    def test_security_decision_composite(self) -> None:
        """SecurityDecision should compose all sub-decisions."""
        decision = SecurityDecision(
            request_id="req-001",
            tool_name="email.read",
            provenance=ProvenanceRecord(
                request_id="req-001", source=ProvenanceSource.USER, confidence=0.9
            ),
            detection=DetectionResult(request_id="req-001"),
            intent=UserIntent(intent_summary="Read emails", confidence=0.9),
            alignment=AlignmentResult(request_id="req-001"),
            risk=RiskResult(request_id="req-001"),
            policy=PolicyDecision(request_id="req-001", action=DecisionAction.ALLOW),
            authorization=AuthorizationDecision(
                request_id="req-001", authorized=True, action=DecisionAction.ALLOW
            ),
            overall_action=DecisionAction.ALLOW,
        )
        assert decision.overall_action == DecisionAction.ALLOW
        assert decision.authorization.authorized is True


class TestExperimentContracts:
    def test_experiment_config(self) -> None:
        config = ExperimentConfig(
            name="Test Experiment",
            attack_types=["direct_injection"],
            num_trials=5,
        )
        assert config.name == "Test Experiment"
        assert config.seed == 42  # Default

    def test_experiment_result(self) -> None:
        config = ExperimentConfig(name="Test")
        result = ExperimentResult(
            experiment_id=config.id,
            config=config,
            metrics={"accuracy": 0.95},
        )
        assert result.metrics["accuracy"] == 0.95


class TestAuditContracts:
    def test_audit_event(self) -> None:
        event = AuditEvent(
            event_type=AuditEventType.TOOL_REQUESTED,
            request_id="req-001",
            tool_name="email.send",
            action=DecisionAction.ALLOW,
        )
        assert event.event_type == AuditEventType.TOOL_REQUESTED
        assert event.id  # Auto-generated
