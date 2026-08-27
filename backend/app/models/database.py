"""
CASML — SQLAlchemy Database Models

These models define the database schema for persistent storage.
Use Alembic migrations for all schema changes.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskModel(Base):
    """A user task / session record."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, default="anonymous")
    request: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


class ToolDefinitionModel(Base):
    """Registered tool definition."""

    __tablename__ = "tool_definitions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="general")
    sensitivity: Mapped[str] = mapped_column(String(50), default="medium")
    parameters_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ToolRequestModel(Base):
    """Record of a tool execution request."""

    __tablename__ = "tool_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    requesting_agent: Mapped[str] = mapped_column(String(255), default="default_agent")
    original_user_request: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SecurityDecisionModel(Base):
    """Record of a security pipeline decision."""

    __tablename__ = "security_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[str] = mapped_column(String(255), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_action: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), default="low")
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    injection_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    aligned: Mapped[bool] = mapped_column(Boolean, default=True)
    authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    full_decision: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditEventModel(Base):
    """Audit trail entry."""

    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tool_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str] = mapped_column(String(255), default="anonymous")
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExperimentRunModel(Base):
    """Record of an experiment run."""

    __tablename__ = "experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ExperimentResultModel(Base):
    """Results from an experiment run."""

    __tablename__ = "experiment_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    confusion_matrix: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    per_sample_results: Mapped[list] = mapped_column(JSON, default=list)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AttackCaseModel(Base):
    """A specific attack test case for experiments."""

    __tablename__ = "attack_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    attack_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    expected_detection: Mapped[bool] = mapped_column(Boolean, default=True)
    tool_name: Mapped[str] = mapped_column(String(255), default="")
    severity: Mapped[str] = mapped_column(String(50), default="medium")
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
