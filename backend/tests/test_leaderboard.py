from .conftest import auth_header


def test_leaderboard_filters(client):
    headers = auth_header(client)
    client.post(
        "/api/v1/brews",
        headers=headers,
        json={
            "coffee_amount": 15,
            "grinder_setting_clicks": 10,
            "temperature_c": 86,
            "brew_time_seconds": 120,
            "press_time_seconds": 30,
            "anti_static_water_microliter": 80,
            "score": 8.8,
            "method": "median",
        },
    )

    response = client.get("/api/v1/leaderboard?minimum_score=8", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["number_of_trials"] == 1
    assert len(payload["items"]) == 1
