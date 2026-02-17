import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin
from coffee_backend.db.models.enums import BrewMethod


class Brew(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "brews"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    bean_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("beans.id"), nullable=True)
    recipe_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("recipes.id"), nullable=True)
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("equipment.id"), nullable=True)
    method: Mapped[BrewMethod] = mapped_column(String(50), index=True)
    parameters: Mapped[dict[str, object]] = mapped_column(JSON)
    extra_data: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    brewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    failed: Mapped[bool] = mapped_column(Boolean, default=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    import_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

    user = relationship("User", back_populates="brews")
    bean = relationship("Bean", back_populates="brews")
    recipe = relationship("Recipe", back_populates="brews")
    equipment = relationship("Equipment", back_populates="brews")
