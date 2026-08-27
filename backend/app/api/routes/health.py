"""
CASML — Health Route

Simple health check endpoint.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Status and timestamp.
    """
    return {
        "status": "healthy",
        "service": "casml",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
