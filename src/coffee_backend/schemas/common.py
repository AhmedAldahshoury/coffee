from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


class TimestampedSchema(BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
