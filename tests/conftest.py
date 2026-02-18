from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from coffee_backend.core.config import Settings
from coffee_backend.db.base import Base
from coffee_backend.db.session import create_engine_from_settings
from coffee_backend.main import create_app


@pytest.fixture(scope="session")
def test_settings(tmp_path_factory: pytest.TempPathFactory) -> Settings:
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    return Settings(database_url=f"sqlite:///{db_path}", jwt_secret="test-secret")


@pytest.fixture(autouse=True)
def reset_db(test_settings: Settings) -> Generator[None, None, None]:
    engine = create_engine_from_settings(test_settings)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    engine.dispose()
    yield


@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    app = create_app(test_settings)
    with TestClient(app) as c:
        yield c
