from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/best")
def best(
    user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> dict[str, dict[str, float | str]]:
    return AnalyticsService(db).best_per_method(user.id)


@router.get("/trend")
def trend(
    user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> list[dict[str, float | str]]:
    return AnalyticsService(db).score_trend(user.id)
