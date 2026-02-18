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


def test_import_csv_invalid_row_is_rejected_with_error(client, tmp_path):
    token = auth_token(client)
    csv_path = tmp_path / "bad_aeropress.csv"
    csv_path.write_text(
        "date,score,grind_size,water_temp,brew_time_sec,unknown_key\n"
        "2024-01-01T10:00:00+00:00,8,10,90,120,oops\n",
        encoding="utf-8",
    )

    response = client.post(
        "/api/v1/import/csv",
        headers={"Authorization": f"Bearer {token}"},
        json={"method": "aeropress", "data_path": str(csv_path)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["imported"] == 0
    assert body["skipped"] == 1
    assert body["errors"] == [
        {
            "row": 2,
            "detail": "Unknown parameter keys",
            "code": "unknown_parameter_keys",
            "fields": {"unknown_key": "unknown parameter"},
        }
    ]
