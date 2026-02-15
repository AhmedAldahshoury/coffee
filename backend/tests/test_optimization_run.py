from .conftest import auth_header


def test_start_and_submit_score(client):
    headers = auth_header(client)
    start = client.post(
        "/api/v1/optimizer/runs/start",
        headers=headers,
        json={"selected_persons": ["A"], "method": "median", "n_trials": 2},
    )
    assert start.status_code == 200
    run = start.json()
    assert run["latest_trial"]["state"] == "suggested"

    submit = client.post(
        f"/api/v1/optimizer/runs/{run['id']}/submit_score",
        headers=headers,
        json={"trial_id": run["latest_trial"]["id"], "score": 8.4},
    )
    assert submit.status_code == 200
    assert submit.json()["trial_count"] == 1
