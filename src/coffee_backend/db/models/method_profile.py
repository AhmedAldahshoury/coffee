from sqlalchemy import JSON, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from coffee_backend.db.base import Base


class MethodProfile(Base):
    __tablename__ = "method_profiles"
    __table_args__ = (
        UniqueConstraint(
            "method_id",
            "variant_id",
            "schema_version",
            name="uq_method_profiles_method_variant_version",
        ),
    )

    method_id: Mapped[str] = mapped_column(String(50), index=True)
    variant_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    parameters: Mapped[list[dict[str, object]]] = mapped_column(JSON)
