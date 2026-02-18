from datetime import datetime, timezone

from fastapi.testclient import TestClient

from coffee_backend.core.config import Settings
from coffee_backend.main import create_app


def auth_token(client: TestClient, email: str = "opt@example.com") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": "pass123"})
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "pass123"})
    return res.json()["access_token"]


def create_brew(client: TestClient, token: str, score: float | None = None) -> str:
    response = client.post(
        "/api/v1/brews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "method": "aeropress",
            "parameters": {"grind_size": 10, "water_temp": 90.0, "brew_time_sec": 120},
            "brewed_at": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "failed": False,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_optimise_suggest_schema(client: TestClient):
    token = auth_token(client)
    response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress"},
    )
    assert response.status_code == 200
    payload = response.json()
    params = payload["suggested_parameters"]
    assert payload["id"]
    assert payload["study_key"].startswith("u:")
    assert isinstance(payload["trial_number"], int)
    assert "dose_g" in params
    assert "water_g" in params


def test_optimisation_suggest_then_apply_increments_completed_trial_count(client: TestClient):
    token = auth_token(client)
    suggest_response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress"},
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

    after_response = client.get(
        "/api/v1/optimisation/insights",
        headers={"Authorization": f"Bearer {token}"},
        params={"study_key": suggestion["study_key"]},
    )
    assert after_response.status_code == 200
    assert after_response.json()["trial_count"] == 1


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


def test_optimisation_invalid_apply_returns_clear_error_code(client: TestClient):
    token = auth_token(client)
    suggest_response = client.post(
        "/api/v1/optimisation/suggest",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress"},
    )
    suggestion_id = suggest_response.json()["id"]
    brew_id = create_brew(client, token)

    response = client.post(
        f"/api/v1/optimisation/suggestions/{suggestion_id}/apply",
        headers={"Authorization": f"Bearer {token}"},
        json={"brew_id": brew_id, "score": 99, "failed": False},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "suggestion_score_out_of_range"


def test_study_key_differs_for_same_method_different_beans(client: TestClient):
    token = auth_token(client)

    bean_1 = client.post(
        "/api/v1/beans",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Bean One"},
    ).json()["id"]
    bean_2 = client.post(
        "/api/v1/beans",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Bean Two"},
    ).json()["id"]

    first = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "bean_id": bean_1},
    )
    second = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "bean_id": bean_2},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["study_key"] != second.json()["study_key"]


def test_study_key_differs_for_v60_vs_aeropress(client: TestClient):
    token = auth_token(client)

    aeropress = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress"},
    )
    v60 = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "v60"},
    )

    assert aeropress.status_code == 200
    assert v60.status_code == 200
    assert aeropress.json()["study_key"] != v60.json()["study_key"]


def test_study_key_differs_for_variants(client: TestClient):
    token = auth_token(client)

    standard = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_standard"},
    )
    inverted = client.post(
        "/api/v1/optimisation/studies",
        headers={"Authorization": f"Bearer {token}"},
        json={"method_id": "aeropress", "variant_id": "aeropress_inverted"},
    )

    assert standard.status_code == 200
    assert inverted.status_code == 200
    assert standard.json()["study_key"] != inverted.json()["study_key"]
