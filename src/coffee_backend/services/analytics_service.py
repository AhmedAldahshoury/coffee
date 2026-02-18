from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from coffee_backend.db.models.brew import Brew


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def best_per_method(self, user_id: UUID) -> dict[str, dict[str, float | str]]:
        rows = self.db.execute(
            select(Brew.method, func.max(Brew.score))
            .where(Brew.user_id == user_id)
            .group_by(Brew.method)
        ).all()
        return {method: {"best_score": score} for method, score in rows if score is not None}

    def score_trend(self, user_id: UUID) -> list[dict[str, float | str]]:
        rows = self.db.execute(
            select(func.date(Brew.brewed_at), func.avg(Brew.score))
            .where(Brew.user_id == user_id, Brew.score.is_not(None))
            .group_by(func.date(Brew.brewed_at))
            .order_by(func.date(Brew.brewed_at))
        ).all()
        return [{"date": str(day), "avg_score": float(avg)} for day, avg in rows if day is not None]
