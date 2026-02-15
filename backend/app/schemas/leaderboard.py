from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    brew_id: int
    user_id: UUID
    score: float
    method: str
    created_at: datetime
    coffee_amount: float
    grinder_setting_clicks: int
    temperature_c: int


class LeaderboardResponse(BaseModel):
    items: list[LeaderboardEntry]
    average_score: float
    number_of_trials: int
    total: int
    page: int
    page_size: int
