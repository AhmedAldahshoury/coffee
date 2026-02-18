def test_list_methods_returns_seeded_variants(client) -> None:
    response = client.get("/api/v1/methods")

    assert response.status_code == 200
    payload = response.json()
    methods = {entry["method_id"]: entry for entry in payload["methods"]}

    assert {"v60", "aeropress"}.issubset(methods.keys())

    aeropress_variants = {variant["variant_id"] for variant in methods["aeropress"]["variants"]}
    assert aeropress_variants == {"aeropress_standard", "aeropress_inverted"}


def test_get_method_profiles_returns_full_schema(client) -> None:
    response = client.get("/api/v1/methods/v60")

    assert response.status_code == 200
    payload = response.json()

    assert payload["method_id"] == "v60"
    assert len(payload["profiles"]) == 1

    v60_profile = payload["profiles"][0]
    assert v60_profile["variant_id"] == "v60_default"
    assert v60_profile["schema_version"] == 1

    ratio_param = next(param for param in v60_profile["parameters"] if param["name"] == "ratio")
    assert ratio_param == {
        "name": "ratio",
        "type": "float",
        "min": 15.0,
        "max": 18.5,
        "step": 0.1,
        "unit": ":1",
        "default": 16.5,
        "description": "Coffee-to-water ratio.",
        "depends_on": None,
    }


def test_get_method_variant_returns_specific_defaults(client) -> None:
    response = client.get("/api/v1/methods/aeropress/aeropress_inverted")

    assert response.status_code == 200
    payload = response.json()

    steep_param = next(param for param in payload["parameters"] if param["name"] == "steep_s")
    stir_param = next(param for param in payload["parameters"] if param["name"] == "stir_count")

    assert steep_param["default"] == 90
    assert stir_param["default"] == 8


def test_get_method_profiles_returns_not_found_for_unknown_method(client) -> None:
    response = client.get("/api/v1/methods/chemex")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
