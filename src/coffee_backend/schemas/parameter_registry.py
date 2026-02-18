from typing import Any

ParameterSpec = dict[str, Any]
MethodParameterRegistry = dict[str, dict[str, ParameterSpec]]

METHOD_PARAMETER_REGISTRY: MethodParameterRegistry = {
    "aeropress": {
        "grind_size": {"type": "int", "min": 1, "max": 15, "required": True},
        "water_temp": {"type": "float", "min": 75.0, "max": 100.0, "required": True},
        "brew_time_sec": {"type": "int", "min": 30, "max": 300, "required": True},
        "coffee_g": {"type": "float", "min": 10.0, "max": 30.0, "required": False},
        "water_g": {"type": "float", "min": 100.0, "max": 350.0, "required": False},
        "agitation": {
            "type": "categorical",
            "choices": ["low", "medium", "high"],
            "required": False,
        },
    },
    "pourover": {
        "grind_size": {"type": "int", "min": 1, "max": 30, "required": True},
        "water_temp": {"type": "float", "min": 80.0, "max": 99.0, "required": True},
        "bloom_time_sec": {"type": "int", "min": 15, "max": 90, "required": True},
        "total_time_sec": {"type": "int", "min": 90, "max": 480, "required": True},
        "coffee_g": {"type": "float", "min": 12.0, "max": 40.0, "required": False},
        "water_g": {"type": "float", "min": 150.0, "max": 600.0, "required": False},
    },
}
