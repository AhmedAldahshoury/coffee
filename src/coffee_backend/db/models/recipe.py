import uuid

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin
from coffee_backend.db.models.enums import BrewMethod


class Recipe(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recipes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    method: Mapped[BrewMethod] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameter_schema: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="recipes")
    brews = relationship("Brew", back_populates="recipe")
