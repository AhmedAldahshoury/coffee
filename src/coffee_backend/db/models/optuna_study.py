import uuid

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin


class StudyContext(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "study_contexts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "method_id",
            "variant_id",
            "bean_id",
            "equipment_id",
            name="uq_study_context_scope",
        ),
        UniqueConstraint("study_key", name="uq_study_context_study_key"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    method_id: Mapped[str] = mapped_column(String(50), index=True)
    variant_id: Mapped[str] = mapped_column(String(100), index=True)
    bean_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("beans.id"), nullable=True)
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("equipment.id"), nullable=True
    )
    study_key: Mapped[str] = mapped_column(String(255), index=True)

    user = relationship("User", back_populates="study_contexts")
    suggestions = relationship("Suggestion", back_populates="study_context")


class Suggestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suggestions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    study_context_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("study_contexts.id", ondelete="CASCADE"),
        index=True,
    )
    brew_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("brews.id"), nullable=True)
    study_key: Mapped[str] = mapped_column(String(255), index=True)
    trial_number: Mapped[int] = mapped_column()
    suggested_parameters: Mapped[dict[str, object]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="issued", index=True)

    user = relationship("User", back_populates="suggestions")
    study_context = relationship("StudyContext", back_populates="suggestions")
