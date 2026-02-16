from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.persistence import Brew, User
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
def get_leaderboard(
    user_id: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    method: str | None = None,
    minimum_score: float | None = None,
    sort_by: str = Query(default="score", pattern="^(score|date)$"),
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaderboardResponse:
    base_query = select(Brew)
    if user_id:
        base_query = base_query.where(Brew.user_id == user_id)
    if date_from:
        base_query = base_query.where(Brew.created_at >= date_from)
    if date_to:
        base_query = base_query.where(Brew.created_at <= date_to)
    if method:
        base_query = base_query.where(Brew.method == method)
    if minimum_score is not None:
        base_query = base_query.where(Brew.score >= minimum_score)

    filtered_subq = base_query.subquery()

    total = db.scalar(select(func.count()).select_from(filtered_subq)) or 0
    avg_score = db.scalar(select(func.avg(filtered_subq.c.score)).select_from(filtered_subq)) or 0.0
    count_trials = db.scalar(select(func.count()).select_from(filtered_subq)) or 0

    if sort_by == "score":
        ordered_query = base_query.order_by(Brew.score.desc())
    else:
        ordered_query = base_query.order_by(Brew.created_at.desc())
    items = list(db.scalars(ordered_query.offset((page - 1) * page_size).limit(page_size)))

    return LeaderboardResponse(
        items=[
            LeaderboardEntry(
                brew_id=item.id,
                user_id=item.user_id,
                score=item.score,
                method=item.method,
                created_at=item.created_at,
                coffee_amount=item.coffee_amount,
                grinder_setting_clicks=item.grinder_setting_clicks,
                temperature_c=item.temperature_c,
            )
            for item in items
        ],
        average_score=float(avg_score),
        number_of_trials=int(count_trials),
        total=int(total),
        page=page,
        page_size=page_size,
    )
