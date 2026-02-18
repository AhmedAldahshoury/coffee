from pydantic import BaseModel

from coffee_backend.schemas.common import TimestampedSchema


class EquipmentCreate(BaseModel):
    method: str
    grinder_model: str | None = None
    filter_type: str | None = None
    kettle: str | None = None
    details: dict[str, str] | None = None


class EquipmentRead(TimestampedSchema, EquipmentCreate):
    pass
