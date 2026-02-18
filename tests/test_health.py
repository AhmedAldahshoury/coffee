from fastapi.testclient import TestClient

from coffee_backend.core.config import Settings
from coffee_backend.main import create_app


def test_health_checks_database(test_settings: Settings) -> None:
    app = create_app(test_settings)
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}
