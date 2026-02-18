from pydantic import BaseModel

from coffee_backend.schemas.common import TimestampedSchema


class RecipeCreate(BaseModel):
    method: str
    name: str
    notes: str | None = None
    parameter_schema: dict[str, object] | None = None


class RecipeRead(TimestampedSchema, RecipeCreate):
    pass


class RecipeStep(BaseModel):
    text: str
    timer_seconds: int | None = None


class RecipeRenderResponse(BaseModel):
    title: str
    equipment: list[str]
    steps: list[RecipeStep]
