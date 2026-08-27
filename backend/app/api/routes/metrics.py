"""
CASML — Metrics & Audit Routes

Endpoints for system metrics and audit log.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.contracts import AuditEvent, AuditEventType, DecisionAction, RiskLevel

router = APIRouter(prefix="/api", tags=["metrics", "audit"])

# In-memory audit store
_audit_events: list[AuditEvent] = []


def log_audit_event(event: AuditEvent) -> None:
    """Append an audit event to the in-memory store."""
    _audit_events.append(event)


@router.get("/metrics")
async def get_metrics() -> dict:
    """Get system metrics.

    Returns aggregate counts and statistics.
    """
    total = len(_audit_events)
    by_type = {}
    for event in _audit_events:
        key = event.event_type.value
        by_type[key] = by_type.get(key, 0) + 1

    return {
        "total_events": total,
        "events_by_type": by_type,
        "tools_registered": 10,  # From mock tools
        "uptime_seconds": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/audit", response_model=list[AuditEvent])
async def get_audit_log(
    limit: int = 100,
    event_type: str | None = None,
) -> list[AuditEvent]:
    """Get audit log entries.

    Args:
        limit: Maximum number of events to return.
        event_type: Filter by event type.
    """
    events = _audit_events

    if event_type:
        try:
            filter_type = AuditEventType(event_type)
            events = [e for e in events if e.event_type == filter_type]
        except ValueError:
            pass

    return events[-limit:]
