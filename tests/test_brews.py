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
            "parameters": {
                "grind_size": 10,
                "water_temp": 90.0,
                "brew_time_sec": 120,
            },
            "brewed_at": datetime.now(timezone.utc).isoformat(),
            "score": 8.5,
            "failed": False,
        },
    )
    assert response.status_code == 201
    assert response.json()["method"] == "aeropress"


def test_create_brew_missing_required_params_returns_422(client):
    token = auth_token(client)
    response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {"grind_size": 10, "water_temp": 90.0},
            "brewed_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "missing_required_parameters"


def test_create_brew_unknown_param_returns_422(client):
    token = auth_token(client)
    response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {
                "grind_size": 10,
                "water_temp": 90.0,
                "brew_time_sec": 120,
                "unknown_key": 1,
            },
            "brewed_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "unknown_parameter_keys"


def test_list_brews_with_pagination(client):
    token = auth_token(client)

    for day in range(1, 6):
        response = client.post(
            "/api/v1/brews",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "method": "aeropress",
                "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
                "brewed_at": f"2024-01-0{day}T10:00:00+00:00",
            },
        )
        assert response.status_code == 201

    response = client.get(
        "/api/v1/brews?page=1&page_size=2&include_total=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_list_brews_with_filtering(client):
    token = auth_token(client)

    client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
            "brewed_at": "2024-01-01T10:00:00+00:00",
            "score": 6.5,
        },
    )
    client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "pourover",
            "parameters": {
                "grind_size": 12,
                "water_temp": 93.0,
                "bloom_time_sec": 40,
                "total_time_sec": 180,
            },
            "brewed_at": "2024-01-03T10:00:00+00:00",
            "score": 9.0,
        },
    )

    response = client.get(
        "/api/v1/brews?method=aeropress&brewed_from=2024-01-01T00:00:00%2B00:00&brewed_to=2024-01-02T23:59:59%2B00:00",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["method"] == "aeropress"
