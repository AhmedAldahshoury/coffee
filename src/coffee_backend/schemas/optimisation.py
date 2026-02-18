from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from coffee_backend.schemas.common import TimestampedSchema


class StudyRequest(BaseModel):
    method_id: str
    variant_id: str | None = None
    bean_id: UUID | None = None
    equipment_id: UUID | None = None


class StudyContextRead(BaseModel):
    study_key: str
    method_id: str
    variant_id: str
    bean_id: UUID | None = None
    equipment_id: UUID | None = None


class SuggestionRead(TimestampedSchema):
    user_id: UUID
    brew_id: UUID | None = None
    study_key: str
    trial_number: int
    suggested_params: dict[str, object]
    actual_params: dict[str, object] | None = None
    status: str


class SuggestRequest(StudyRequest):
    pass


class ApplySuggestionRequest(BaseModel):
    brew_id: UUID
    score: float | None = None
    failed: bool = False


class OptimisationInsight(BaseModel):
    study_key: str
    trial_count: int
    parameter_importance: dict[str, float]
    generated_at: datetime
