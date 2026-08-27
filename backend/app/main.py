"""
CASML — FastAPI Application Entry Point

Context-Aware Security Middleware Layer
Protects tool-using LLM agents against prompt injection and unauthorized actions.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.tools.mock_tools import register_mock_tools

# ── Route Imports ────────────────────────────────────────
from app.api.routes.health import router as health_router
from app.api.routes.agent import router as agent_router
from app.api.routes.security import router as security_router
from app.api.routes.tools import router as tools_router
from app.api.routes.experiments import router as experiments_router
from app.api.routes.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown events."""
    # ── Startup ──────────────────────────────────────
    register_mock_tools()
    print(f"🛡️  CASML v0.1.0 started — {settings.app_env} mode")
    print(f"📊 Registered {10} mock tools")

    yield

    # ── Shutdown ─────────────────────────────────────
    print("🛡️  CASML shutting down")


# ── Application ──────────────────────────────────────────
app = FastAPI(
    title="CASML — Context-Aware Security Middleware Layer",
    description=(
        "Security middleware for tool-using LLM agents. "
        "Protects against indirect prompt injection and unauthorized tool execution."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────
app.include_router(health_router)
app.include_router(agent_router)
app.include_router(security_router)
app.include_router(tools_router)
app.include_router(experiments_router)
app.include_router(metrics_router)
