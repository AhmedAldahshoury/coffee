from typing import Any

METHOD_PARAMETER_REGISTRY: dict[str, dict[str, dict[str, Any]]] = {
    "aeropress": {
        "grind_size": {"type": "int", "min": 1, "max": 15},
        "water_temp": {"type": "float", "min": 75.0, "max": 100.0},
        "brew_time_sec": {"type": "int", "min": 30, "max": 300},
        "coffee_g": {"type": "float", "min": 10.0, "max": 30.0},
        "water_g": {"type": "float", "min": 100.0, "max": 350.0},
        "agitation": {"type": "categorical", "choices": ["low", "medium", "high"]},
    },
    "pourover": {
        "grind_size": {"type": "int", "min": 1, "max": 30},
        "water_temp": {"type": "float", "min": 80.0, "max": 99.0},
        "bloom_time_sec": {"type": "int", "min": 15, "max": 90},
        "total_time_sec": {"type": "int", "min": 90, "max": 480},
        "coffee_g": {"type": "float", "min": 12.0, "max": 40.0},
        "water_g": {"type": "float", "min": 150.0, "max": 600.0},
    },
}
