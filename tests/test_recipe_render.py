from fastapi.testclient import TestClient


def test_render_v60_deterministic_steps(client: TestClient):
    response = client.get(
        "/api/v1/recipes/render",
        params={
            "method_id": "v60",
            "variant_id": "v60_default",
            "params": (
                '{"dose_g":15,"ratio":16,"bloom_ratio":2.5,'
                '"bloom_s":30,"pours":3,"total_time_s":180}'
            ),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "V60 (v60_default)"
    assert body["steps"] == [
        {"text": "Bloom: pour 38g water and wait 30s.", "timer_seconds": 30},
        {"text": "Pour pulse 1: add water to ~76g total by 80s.", "timer_seconds": 50},
        {"text": "Pour pulse 2: add water to ~114g total by 130s.", "timer_seconds": 50},
        {"text": "Pour pulse 3: add water to ~152g total by 180s.", "timer_seconds": 50},
    ]


def test_render_aeropress_deterministic_steps_from_query_kv(client: TestClient):
    response = client.get(
        "/api/v1/recipes/render",
        params=[
            ("method_id", "aeropress"),
            ("variant_id", "aeropress_standard"),
            ("param", "water_g=220"),
            ("param", "stir_count=7"),
            ("param", "steep_s=75"),
            ("param", "plunge_s=30"),
        ],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Aeropress (aeropress_standard)"
    assert body["steps"] == [
        {"text": "Add 220g water to the chamber.", "timer_seconds": None},
        {"text": "Stir 7 times to evenly saturate grounds.", "timer_seconds": None},
        {"text": "Steep for 75s.", "timer_seconds": 75},
        {"text": "Plunge gently for 30s.", "timer_seconds": 30},
    ]
