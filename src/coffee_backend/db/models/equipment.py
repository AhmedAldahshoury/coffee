import uuid

from sqlalchemy import ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin
from coffee_backend.db.models.enums import BrewMethod


class Equipment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "equipment"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    method: Mapped[BrewMethod] = mapped_column(String(50), index=True)
    grinder_model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    filter_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kettle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="equipment")
    brews = relationship("Brew", back_populates="equipment")
