import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coffee_backend.db.base import Base
from coffee_backend.db.models.common import TimestampMixin, UUIDMixin


class Bean(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "beans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    roaster: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    process: Mapped[str | None] = mapped_column(String(255), nullable=True)
    roast_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    roast_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="beans")
    brews = relationship("Brew", back_populates="bean")
