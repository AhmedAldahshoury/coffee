from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from coffee_backend.core.config import get_settings
from coffee_backend.db.session import create_engine_from_settings, create_sessionmaker


@contextmanager
def get_cli_db_session() -> Generator[Session, None, None]:
    engine = create_engine_from_settings(get_settings())
    session_factory = create_sessionmaker(engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
