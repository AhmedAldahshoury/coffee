from pathlib import Path
from uuid import uuid4

from coffee_backend.schemas.import_export import CSVImportRequest
from coffee_backend.services.import_export_service import ImportExportService


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


def test_import_csv_batches_commits(client, tmp_path, monkeypatch):
    csv_path = tmp_path / "batch.csv"
    csv_path.write_text(
        "date,score,grind_size,water_temp,brew_time_sec\n"
        "2024-01-01T10:00:00+00:00,8,10,90,120\n"
        "2024-01-02T10:00:00+00:00,7,10,90,120\n"
        "2024-01-03T10:00:00+00:00,9,10,90,120\n",
        encoding="utf-8",
    )

    class FakeSession:
        def __init__(self):
            self.add_count = 0
            self.commit_count = 0
            self.flush_count = 0

        def scalar(self, _query):
            return None

        def add(self, _obj):
            self.add_count += 1

        def flush(self):
            self.flush_count += 1

        def commit(self):
            self.commit_count += 1

    fake_db = FakeSession()
    monkeypatch.setattr(ImportExportService, "BATCH_SIZE", 2)

    result = ImportExportService(fake_db).import_csv(
        uuid4(), CSVImportRequest(method="aeropress", data_path=str(csv_path))
    )

    assert result.processed == 3
    assert result.inserted == 3
    assert result.imported == 3
    assert result.skipped == 0
    assert fake_db.add_count == 3
    assert fake_db.flush_count == 2
    assert fake_db.commit_count == 2
