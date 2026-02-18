from datetime import datetime, timezone

from fastapi.testclient import TestClient

from coffee_backend.core.config import Settings
from coffee_backend.main import create_app


def auth_token(client: TestClient, email: str = "opt@example.com") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": "pass123"})
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "pass123"})
    return res.json()["access_token"]


def create_brew(
    client: TestClient,
    token: str,
    *,
    method: str = "aeropress",
    variant_id: str | None = "aeropress_standard",
    bean_id: str | None = None,
    equipment_id: str | None = None,
    score: float | None = 8.0,
) -> str:
    response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": method,
            "variant_id": variant_id,
            "bean_id": bean_id,
            "equipment_id": equipment_id,
            "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
            "brewed_at": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "status": "ok",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_suggest_uses_correct_schema_for_v60_vs_aeropress(client: TestClient):
    token = auth_token(client)

    aeropress = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    )
    assert aeropress.status_code == 200
    aeropress_params = aeropress.json()["suggested_params"]
    assert "plunge_s" in aeropress_params
    assert "total_time_s" not in aeropress_params

    v60 = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "v60", "variant_id": "v60_default"},
    )
    assert v60.status_code == 200
    v60_params = v60.json()["suggested_params"]
    assert "total_time_s" in v60_params
    assert "plunge_s" not in v60_params


def test_optimisation_suggest_then_apply_increments_completed_trial_count(client: TestClient):
    token = auth_token(client)
    suggest_response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    )
    assert suggest_response.status_code == 200
    suggestion = suggest_response.json()

    before_response = client.get(
        "/api/v1/optimisation/insights",
        headers={"Authorization": f"Bearer {token}"},
        params={"study_key": suggestion["study_key"]},
    )
    assert before_response.status_code == 200
    assert before_response.json()["trial_count"] == 0

    brew_id = create_brew(client, token)
    apply_response = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion['id']}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": brew_id, "score": 8.7, "failed": False},
    )
    assert apply_response.status_code == 200
    assert apply_response.json()["status"] == "applied"
    assert apply_response.json()["actual_params"] is not None

    after_response = client.get(
        "/api/v1/optimisation/insights",
        headers={"Authorization": f"Bearer {token}"},
        params={"study_key": suggestion["study_key"]},
    )
    assert after_response.status_code == 200
    assert after_response.json()["trial_count"] == 1


def test_apply_twice_fails(client: TestClient):
    token = auth_token(client)
    suggestion = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    ).json()
    brew_id = create_brew(client, token)

    first = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion['id']}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": brew_id, "score": 8.5, "failed": False},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion['id']}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": brew_id, "score": 8.5, "failed": False},
    )
    assert second.status_code == 409
    assert second.json()["code"] == "suggestion_already_applied"


def test_context_mismatch_fails(client: TestClient):
    token = auth_token(client)
    suggestion = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    ).json()

    mismatched_brew_id = create_brew(
        client,
        token,
        method="aeropress",
        variant_id="aeropress_inverted",
    )
    apply = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion['id']}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": mismatched_brew_id, "score": 8.0, "failed": False},
    )
    assert apply.status_code == 422
    assert apply.json()["code"] == "suggestion_context_mismatch"


def test_failed_brew_records_low_objective(client: TestClient):
    token = auth_token(client)
    suggest_response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    )
    suggestion = suggest_response.json()
    brew_id = create_brew(client, token, score=None)

    apply_response = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion['id']}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": brew_id, "failed": True},
    )
    assert apply_response.status_code == 200

    insights_response = client.get(
        "/api/v1/optimisation/insights",
        headers={"Authorization": f"Bearer {token}"},
        params={"study_key": suggestion["study_key"]},
    )
    assert insights_response.status_code == 200
    assert insights_response.json()["trial_count"] == 1


def test_optimisation_study_persists_across_app_sessions(test_settings: Settings):
    app = create_app(test_settings)
    with TestClient(app) as client:
        token = auth_token(client, email="persist@example.com")
        first_suggest = client.post(
            "/api/v1/optimisation/suggest",
            headers={"Authorization": f"Bearer {token}"},
            json={"method_id": "aeropress"},
        )
        assert first_suggest.status_code == 200
        first_payload = first_suggest.json()

    app = create_app(test_settings)
    with TestClient(app) as client:
        token = auth_token(client, email="persist@example.com")
        second_suggest = client.post(
            "/api/v1/optimisation/suggest",
            headers={"Authorization": f"Bearer {token}"},
            json={"method_id": "aeropress"},
        )
        assert second_suggest.status_code == 200
        second_payload = second_suggest.json()

    assert second_payload["study_key"] == first_payload["study_key"]
    assert second_payload["trial_number"] > first_payload["trial_number"]


def test_warm_start_is_idempotent(client: TestClient):
    token = auth_token(client, email="warmstart@example.com")

    create_brew(client, token, score=7.1)
    create_brew(client, token, score=8.4)

    payload = {"method_id": "aeropress", "variant_id": "aeropress_standard", "limit": 10}
    first = client.post(
        "/api/v1/optimisation/warm_start",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert first.status_code == 200
    assert first.json()["added"] == 2

    second = client.post(
        "/api/v1/optimisation/warm_start",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert second.status_code == 200
    assert second.json()["added"] == 0
    assert second.json()["skipped"] == 2

    suggest_response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    )
    assert suggest_response.status_code == 200
    study_key = suggest_response.json()["study_key"]

    insights = client.get(
        "/api/v1/optimisation/insights",
        headers={"Authorization": f"Bearer {token}"},
        params={"study_key": study_key},
    )
    assert insights.status_code == 200
    assert insights.json()["trial_count"] == 2
