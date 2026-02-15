import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"

from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def auth_header(client: TestClient) -> dict[str, str]:
    register = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "password123"})
    token = register.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
