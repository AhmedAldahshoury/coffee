from datetime import date

from pydantic import BaseModel

from coffee_backend.schemas.common import TimestampedSchema


class BeanCreate(BaseModel):
    name: str
    roaster: str | None = None
    origin: str | None = None
    process: str | None = None
    roast_level: str | None = None
    roast_date: date | None = None
    notes: str | None = None


class BeanRead(TimestampedSchema, BeanCreate):
    pass
