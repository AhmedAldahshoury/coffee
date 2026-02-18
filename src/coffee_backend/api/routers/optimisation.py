from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.optimisation import (
    ApplySuggestionRequest,
    OptimisationInsight,
    StudyRequest,
    SuggestionRead,
)
from coffee_backend.services.optimisation_service import OptimisationService

router = APIRouter(prefix="/optimisation", tags=["optimisation"])


@router.post("/studies")
def create_study(
    payload: StudyRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    service = OptimisationService(db)
    study_key = service.ensure_study(user.id, payload)
    return {"study_key": study_key}


@router.post("/suggest", response_model=SuggestionRead)
def suggest(
    payload: StudyRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return OptimisationService(db).suggest(user.id, payload)


@router.post("/suggestions/{suggestion_id}/apply", response_model=SuggestionRead)
def apply_suggestion(
    suggestion_id: UUID,
    payload: ApplySuggestionRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return OptimisationService(db).apply(
        user.id,
        suggestion_id,
        payload.brew_id,
        payload.score,
        payload.failed,
    )


@router.get("/insights", response_model=OptimisationInsight)
def insights(
    study_key: Annotated[str, Query()],
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OptimisationInsight:
    return OptimisationService(db).insights(study_key)
