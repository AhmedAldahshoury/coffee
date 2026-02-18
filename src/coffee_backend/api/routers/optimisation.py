import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.optimisation import (
    ApplySuggestionRequest,
    OptimisationInsight,
    StudyContextRead,
    StudyRequest,
    SuggestionRead,
    WarmStartRequest,
    WarmStartResponse,
)
from coffee_backend.services.optimisation_service import OptimisationService

router = APIRouter(prefix="/optimisation", tags=["optimisation"])
logger = logging.getLogger(__name__)


@router.post("/studies", response_model=StudyContextRead)
def create_study(
    payload: Annotated[
        StudyRequest,
        Body(
            examples=[
                {
                    "method_id": "v60",
                    "variant_id": "v60_default",
                    "bean_id": None,
                    "equipment_id": None,
                }
            ]
        ),
    ],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyContextRead:
    service = OptimisationService(db)
    study_context = service.ensure_study_context(user.id, payload)
    logger.info(
        "optimisation.study.requested",
        extra={"user_id": str(user.id), "study_key": study_context.study_key},
    )
    return StudyContextRead(
        study_key=study_context.study_key,
        method_id=study_context.method_id,
        variant_id=study_context.variant_id,
        bean_id=study_context.bean_id,
        equipment_id=study_context.equipment_id,
    )


@router.post("/warm_start", response_model=WarmStartResponse)
def warm_start(
    payload: Annotated[
        WarmStartRequest,
        Body(
            examples=[
                {
                    "method_id": "aeropress",
                    "variant_id": "aeropress_standard",
                    "bean_id": None,
                    "equipment_id": None,
                    "limit": 20,
                }
            ]
        ),
    ],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WarmStartResponse:
    logger.info(
        "optimisation.warm_start.requested",
        extra={"user_id": str(user.id), "method_id": payload.method_id},
    )
    return OptimisationService(db).warm_start(user.id, payload)


@router.post("/suggest", response_model=SuggestionRead)
def suggest(
    payload: Annotated[
        StudyRequest,
        Body(examples=[{"method_id": "aeropress", "variant_id": "aeropress_standard"}]),
    ],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    logger.info(
        "optimisation.suggest.requested",
        extra={"user_id": str(user.id), "method_id": payload.method_id},
    )
    return OptimisationService(db).suggest(user.id, payload)


@router.post("/suggestions/{suggestion_id}/apply", response_model=SuggestionRead)
def apply_suggestion(
    suggestion_id: UUID,
    payload: ApplySuggestionRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    logger.info(
        "optimisation.apply.requested",
        extra={
            "user_id": str(user.id),
            "suggestion_id": str(suggestion_id),
            "brew_id": str(payload.brew_id),
        },
    )
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
