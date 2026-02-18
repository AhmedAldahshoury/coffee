from datetime import datetime, timezone


def auth_token(client):
    client.post("/api/v1/auth/register", json={"email": "brew@example.com", "password": "pass123"})
    res = client.post(
        "/api/v1/auth/login", json={"email": "brew@example.com", "password": "pass123"}
    )
    return res.json()["access_token"]


def test_create_brew(client):
    token = auth_token(client)
    response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
            "brewed_at": datetime.now(timezone.utc).isoformat(),
            "score": 8.5,
            "failed": False,
        },
    )
    assert response.status_code == 201
    assert response.json()["method"] == "aeropress"
