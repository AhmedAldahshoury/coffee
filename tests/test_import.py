from pathlib import Path


def auth_token(client):
    client.post("/api/v1/auth/register", json={"email": "imp@example.com", "password": "pass123"})
    res = client.post(
        "/api/v1/auth/login", json={"email": "imp@example.com", "password": "pass123"}
    )
    return res.json()["access_token"]


def test_import_csv(client):
    token = auth_token(client)
    path = str(Path("aeropress.data.csv").resolve())
    response = client.post(
        "/api/v1/import/csv",
        headers={"Authorization": f"Bearer {token}"},
        json={"method": "aeropress", "data_path": path},
    )
    assert response.status_code == 200
    assert response.json()["imported"] >= 1
