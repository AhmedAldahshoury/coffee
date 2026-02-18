from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from coffee_backend.db.base import Base


class MethodProfile(Base):
    __tablename__ = "method_profiles"
    method_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    variant_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    schema_version: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    parameters: Mapped[list[dict[str, object]]] = mapped_column(JSON)
