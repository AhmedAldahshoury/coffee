from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_current_user, get_interactive_optimizer_service
from app.models.persistence import Trial, User
from app.schemas.interactive_optimizer import (
    OptimizationRunResponse,
    StartOptimizationRequest,
    SubmitScoreRequest,
    TrialResponse,
)
from app.services.interactive_optimizer import InteractiveOptimizerService

router = APIRouter(prefix="/optimizer/runs", tags=["Interactive Optimizer"])


def _serialize_run(service: InteractiveOptimizerService, run) -> OptimizationRunResponse:
    latest_trial = service._latest_trial(run.id)
    latest = None
    if latest_trial:
        latest = TrialResponse(
            id=latest_trial.id,
            trial_number=latest_trial.trial_number,
            parameters=latest_trial.parameters,
            score=latest_trial.score,
            state=latest_trial.state,
        )
    return OptimizationRunResponse(
        id=run.id,
        status=run.status,
        best_score=run.best_score,
        best_params=run.best_params,
        trial_count=run.trial_count,
        n_trials=run.n_trials,
        method=run.method,
        selected_persons=run.selected_persons,
        created_at=run.created_at,
        latest_trial=latest,
    )


@router.post("/start", response_model=OptimizationRunResponse)
def start_run(
    payload: StartOptimizationRequest,
    user: User = Depends(get_current_user),
    service: InteractiveOptimizerService = Depends(get_interactive_optimizer_service),
) -> OptimizationRunResponse:
    run = service.start_run(user, payload.selected_persons, payload.method, payload.n_trials)
    return _serialize_run(service, run)


@router.post("/{run_id}/submit_score", response_model=OptimizationRunResponse)
def submit_score(
    run_id: UUID,
    payload: SubmitScoreRequest,
    user: User = Depends(get_current_user),
    service: InteractiveOptimizerService = Depends(get_interactive_optimizer_service),
) -> OptimizationRunResponse:
    run = service.get_run(run_id, user)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    updated = service.submit_score(run, payload.trial_id, payload.score)
    return _serialize_run(service, updated)


@router.get("/{run_id}", response_model=OptimizationRunResponse)
def get_run(
    run_id: UUID,
    user: User = Depends(get_current_user),
    service: InteractiveOptimizerService = Depends(get_interactive_optimizer_service),
) -> OptimizationRunResponse:
    run = service.get_run(run_id, user)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _serialize_run(service, run)


@router.get("", response_model=list[OptimizationRunResponse])
def list_runs(
    user: User = Depends(get_current_user),
    service: InteractiveOptimizerService = Depends(get_interactive_optimizer_service),
) -> list[OptimizationRunResponse]:
    return [_serialize_run(service, run) for run in service.list_runs(user)]


@router.get("/{run_id}/events")
def stream_events(
    run_id: UUID,
    user: User = Depends(get_current_user),
    service: InteractiveOptimizerService = Depends(get_interactive_optimizer_service),
) -> StreamingResponse:
    run = service.get_run(run_id, user)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return StreamingResponse(service.stream_events(run), media_type="text/event-stream")
