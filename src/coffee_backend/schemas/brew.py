from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from coffee_backend.schemas.common import TimestampedSchema


class BrewCreate(BaseModel):
    bean_id: UUID | None = None
    recipe_id: UUID | None = None
    equipment_id: UUID | None = None
    method: str
    parameters: dict[str, object] = Field(default_factory=dict)
    brewed_at: datetime
    score: float | None = None
    failed: bool = False
    comments: str | None = None
    tags: list[str] | None = None
    extra_data: dict[str, object] | None = None


class BrewRead(TimestampedSchema, BrewCreate):
    pass
