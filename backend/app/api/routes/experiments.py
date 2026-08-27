"""
CASML — Experiment Routes

Endpoints for running and viewing security experiments.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.contracts import ExperimentConfig, ExperimentResult

router = APIRouter(prefix="/api/experiments", tags=["experiments"])

# In-memory store for mock experiments
_experiments: list[ExperimentResult] = []


class ExperimentRunRequest(BaseModel):
    """Request body for running an experiment."""

    name: str = Field(..., description="Experiment name")
    description: str = Field(default="")
    attack_types: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)
    num_trials: int = Field(default=1, ge=1)
    seed: int = 42


@router.post("/run", response_model=ExperimentResult)
async def run_experiment(request: ExperimentRunRequest) -> ExperimentResult:
    """Run a security experiment.

    Currently returns mock results. Will be replaced with
    actual experiment execution in the research engine.
    """
    config = ExperimentConfig(
        name=request.name,
        description=request.description,
        attack_types=request.attack_types,
        parameters=request.parameters,
        num_trials=request.num_trials,
        seed=request.seed,
    )

    # Mock experiment result
    result = ExperimentResult(
        experiment_id=config.id,
        config=config,
        metrics={
            "accuracy": 0.95,
            "precision": 0.93,
            "recall": 0.97,
            "f1_score": 0.95,
            "false_positive_rate": 0.02,
            "false_negative_rate": 0.03,
        },
        confusion_matrix={
            "true_positive": 97,
            "true_negative": 95,
            "false_positive": 2,
            "false_negative": 3,
        },
        duration_seconds=12.5,
        timestamp=datetime.utcnow(),
        notes="Mock experiment result — replace with actual implementation",
    )

    _experiments.append(result)
    return result


@router.get("", response_model=list[ExperimentResult])
async def list_experiments() -> list[ExperimentResult]:
    """List all experiment runs."""
    return _experiments
