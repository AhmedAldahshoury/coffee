from collections.abc import Generator
from typing import Any

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from coffee_backend.core.config import Settings, get_settings


def create_engine_from_settings(settings: Settings) -> Engine:
    connect_args: dict[str, Any] = (
        {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    )
    return create_engine(settings.database_url, echo=False, future=True, connect_args=connect_args)


def create_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db_state(state: Any, settings: Settings | None = None) -> None:
    resolved_settings = settings or get_settings()
    engine = create_engine_from_settings(resolved_settings)
    state.db_engine = engine
    state.db_sessionmaker = create_sessionmaker(engine)


def dispose_db_state(state: Any) -> None:
    engine: Engine | None = getattr(state, "db_engine", None)
    if engine is not None:
        engine.dispose()


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory = getattr(request.app.state, "db_sessionmaker", None)
    if session_factory is None:
        raise RuntimeError("Database sessionmaker is not initialised on app.state")

    db = session_factory()
    try:
        yield db
    finally:
        db.close()
