def auth_token(client):
    client.post("/api/v1/auth/register", json={"email": "opt@example.com", "password": "pass123"})
    res = client.post("/api/v1/auth/login", json={"email": "opt@example.com", "password": "pass123"})
    return res.json()["access_token"]


def test_optimise_suggest_schema(client):
    token = auth_token(client)
    response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method": "aeropress"},
    )
    assert response.status_code == 200
    params = response.json()["suggested_parameters"]
    assert "grind_size" in params
    assert "water_temp" in params
