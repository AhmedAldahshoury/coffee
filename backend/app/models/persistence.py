from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    brews: Mapped[list[Brew]] = relationship(back_populates="user", cascade="all, delete-orphan")
    optimization_runs: Mapped[list[OptimizationRun]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Brew(Base):
    __tablename__ = "brews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    coffee_amount: Mapped[float] = mapped_column(Float)
    grinder_setting_clicks: Mapped[int] = mapped_column(Integer)
    temperature_c: Mapped[int] = mapped_column(Integer)
    brew_time_seconds: Mapped[int] = mapped_column(Integer)
    press_time_seconds: Mapped[int] = mapped_column(Integer)
    anti_static_water_microliter: Mapped[int] = mapped_column(Integer)
    method: Mapped[str] = mapped_column(String(32), default="median", index=True)
    score: Mapped[float] = mapped_column(Float, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="brews")


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    method: Mapped[str] = mapped_column(String(32), default="median")
    selected_persons: Mapped[list[str]] = mapped_column(JSON, default=list)
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    trial_count: Mapped[int] = mapped_column(Integer, default=0)
    n_trials: Mapped[int] = mapped_column(Integer, default=50)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="optimization_runs")
    trials: Mapped[list[Trial]] = relationship(back_populates="optimization_run", cascade="all, delete-orphan")


class Trial(Base):
    __tablename__ = "trials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    optimization_run_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("optimization_runs.id"), index=True)
    parameters: Mapped[dict] = mapped_column(JSON)
    score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    state: Mapped[str] = mapped_column(String(32), default="suggested", index=True)
    trial_number: Mapped[int] = mapped_column(Integer)

    optimization_run: Mapped[OptimizationRun] = relationship(back_populates="trials")

    __table_args__ = (
        UniqueConstraint("optimization_run_id", "trial_number", name="uq_run_trial_number"),
        Index("ix_trials_run_state", "optimization_run_id", "state"),
    )
