from datetime import datetime, timezone

from fastapi.testclient import TestClient

from coffee_backend.core.config import Settings
from coffee_backend.main import create_app


def _auth_token(client: TestClient) -> str:
    client.post("/api/v1/auth/register", json={"email": "life@example.com", "password": "pass123"})
    response = client.post(
        "/api/v1/auth/login", json={"email": "life@example.com", "password": "pass123"}
    )
    return response.json()["access_token"]


def test_app_start_with_test_database_url(test_settings: Settings) -> None:
    app = create_app(test_settings)
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}


def test_create_and_read_brew_in_single_client_session(client: TestClient) -> None:
    token = _auth_token(client)
    create_response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
            "brewed_at": datetime.now(timezone.utc).isoformat(),
            "score": 8.0,
            "failed": False,
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/brews", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
