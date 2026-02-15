from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StartOptimizationRequest(BaseModel):
    selected_persons: list[str] = Field(default_factory=list)
    method: str = Field(default="median")
    n_trials: int = Field(default=50, ge=1, le=200)

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        valid = {"mean", "median", "lowest", "highest"}
        if value not in valid:
            raise ValueError(f"method must be one of {sorted(valid)}")
        return value


class SubmitScoreRequest(BaseModel):
    trial_id: int
    score: float = Field(ge=0, le=10)


class TrialResponse(BaseModel):
    id: int
    trial_number: int
    parameters: dict
    score: float | None
    state: str


class OptimizationRunResponse(BaseModel):
    id: UUID
    status: str
    best_score: float | None
    best_params: dict | None
    trial_count: int
    n_trials: int
    method: str
    selected_persons: list[str]
    created_at: datetime
    latest_trial: TrialResponse | None = None


class OptimizationEvent(BaseModel):
    trial_number: int
    best_score: float | None
    best_parameters: dict | None
    last_trial_parameters: dict | None
    last_trial_score: float | None
    run_status: str
