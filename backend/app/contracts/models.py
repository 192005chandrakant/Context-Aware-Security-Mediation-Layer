"""
CASML — Shared Pydantic Contract Models

These 13+ models define the interfaces between all CASML subsystems.
They are the SINGLE SOURCE OF TRUTH for data flowing through the pipeline.

Developers MUST use these contracts for all inter-module communication.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enums
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class RiskLevel(str, Enum):
    """Risk classification levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionAction(str, Enum):
    """Possible security decisions."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    SANDBOX = "sandbox"


class ProvenanceSource(str, Enum):
    """Origin classification of content."""

    USER = "user"
    AGENT = "agent"
    LLM = "llm"
    TOOL_OUTPUT = "tool_output"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class AuditEventType(str, Enum):
    """Types of audit events."""

    TOOL_REQUESTED = "tool_requested"
    SECURITY_ANALYSIS = "security_analysis"
    TOOL_APPROVED = "tool_approved"
    TOOL_DENIED = "tool_denied"
    TOOL_EXECUTED = "tool_executed"
    TOOL_FAILED = "tool_failed"
    INJECTION_DETECTED = "injection_detected"
    POLICY_VIOLATION = "policy_violation"
    EXPERIMENT_STARTED = "experiment_started"
    EXPERIMENT_COMPLETED = "experiment_completed"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tool Contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ToolRequest(BaseModel):
    """A proposed tool invocation from the agent.

    This is the primary input to the CASML pipeline.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str = Field(..., description="Fully qualified tool name, e.g. 'email.send'")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool call arguments")
    requesting_agent: str = Field(default="default_agent", description="ID of the requesting agent")
    original_user_request: str = Field(default="", description="The user's original request text")
    context_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional context (conversation history, etc.)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ToolResponse(BaseModel):
    """Result of tool execution."""

    request_id: str = Field(..., description="ID of the originating ToolRequest")
    tool_name: str
    success: bool
    result: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    sandboxed: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security Pipeline Contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class SecurityContext(BaseModel):
    """Context information provided alongside a ToolRequest for security analysis."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="anonymous")
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    previous_tool_calls: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserIntent(BaseModel):
    """Parsed user intent from the original request."""

    intent_summary: str = Field(..., description="Natural language summary of inferred intent")
    confidence: float = Field(ge=0.0, le=1.0, description="Intent inference confidence")
    extracted_entities: dict[str, Any] = Field(default_factory=dict)
    intent_category: str = Field(default="general")
    raw_request: str = Field(default="")


class ProvenanceRecord(BaseModel):
    """Provenance analysis of a tool request — where did the instruction come from?"""

    request_id: str
    source: ProvenanceSource
    confidence: float = Field(ge=0.0, le=1.0)
    chain: list[str] = Field(
        default_factory=list,
        description="Provenance chain, e.g. ['user', 'agent', 'llm']",
    )
    tainted: bool = Field(
        default=False,
        description="Whether the request chain contains external/untrusted content",
    )
    details: dict[str, Any] = Field(default_factory=dict)


class DetectionResult(BaseModel):
    """Output of the injection detection module."""

    request_id: str
    injection_detected: bool = False
    injection_type: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    indicators: list[str] = Field(default_factory=list)
    model_scores: dict[str, float] = Field(default_factory=dict)
    details: dict[str, Any] = Field(default_factory=dict)


class AlignmentResult(BaseModel):
    """Output of the intent/action alignment engine."""

    request_id: str
    aligned: bool = True
    alignment_score: float = Field(ge=0.0, le=1.0, default=1.0)
    user_intent: str = ""
    proposed_action: str = ""
    misalignment_reasons: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class RiskResult(BaseModel):
    """Output of the risk scoring engine."""

    request_id: str
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = Field(ge=0.0, le=1.0, default=0.0)
    component_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown: provenance, injection, alignment, tool_sensitivity",
    )
    explanation: str = ""


class PolicyDecision(BaseModel):
    """Output of the policy engine."""

    request_id: str
    action: DecisionAction = DecisionAction.DENY
    matched_policies: list[str] = Field(default_factory=list)
    overrides: list[str] = Field(default_factory=list)
    explanation: str = ""


class AuthorizationDecision(BaseModel):
    """Final authorization decision from the gateway."""

    request_id: str
    authorized: bool = False
    action: DecisionAction = DecisionAction.DENY
    requires_sandbox: bool = False
    explanation: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SecurityDecision(BaseModel):
    """Composite security verdict — the full output of the CASML pipeline."""

    request_id: str
    tool_name: str
    provenance: ProvenanceRecord
    detection: DetectionResult
    intent: UserIntent
    alignment: AlignmentResult
    risk: RiskResult
    policy: PolicyDecision
    authorization: AuthorizationDecision
    overall_action: DecisionAction = DecisionAction.DENY
    processing_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Experiment Contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ExperimentConfig(BaseModel):
    """Configuration for an experiment run."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    attack_types: list[str] = Field(default_factory=list)
    model_configs: dict[str, Any] = Field(default_factory=dict)
    dataset_path: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    num_trials: int = Field(default=1, ge=1)
    seed: int = 42


class ExperimentResult(BaseModel):
    """Results from an experiment run."""

    experiment_id: str
    config: ExperimentConfig
    metrics: dict[str, float] = Field(default_factory=dict)
    confusion_matrix: dict[str, int] | None = None
    per_sample_results: list[dict[str, Any]] = Field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Audit Contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AuditEvent(BaseModel):
    """An entry in the security audit trail."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType
    request_id: str | None = None
    tool_name: str | None = None
    user_id: str = "anonymous"
    action: DecisionAction | None = None
    risk_level: RiskLevel | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
