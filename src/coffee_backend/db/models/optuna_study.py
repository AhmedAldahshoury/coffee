import uuid

from sqlalchemy import JSON, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin


class Suggestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suggestions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    brew_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("brews.id"), nullable=True)
    study_key: Mapped[str] = mapped_column(String(255), index=True)
    trial_number: Mapped[int] = mapped_column()
    suggested_parameters: Mapped[dict[str, object]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="issued", index=True)

    user = relationship("User", back_populates="suggestions")
