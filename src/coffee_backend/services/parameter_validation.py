from coffee_backend.core.exceptions import ValidationError
from coffee_backend.schemas.parameter_registry import METHOD_PARAMETER_REGISTRY


def validate_method_parameters(method: str, params: dict[str, object]) -> None:
    schema = METHOD_PARAMETER_REGISTRY.get(method)
    if schema is None:
        raise ValidationError(f"Unsupported method: {method}")
    for name, rules in schema.items():
        if name not in params:
            continue
        value = params[name]
        value_type = rules["type"]
        if value_type == "int":
            if not isinstance(value, int):
                raise ValidationError(f"{name} must be int")
            if value < rules["min"] or value > rules["max"]:
                raise ValidationError(f"{name} out of range")
        elif value_type == "float":
            if not isinstance(value, (float, int)):
                raise ValidationError(f"{name} must be number")
            f = float(value)
            if f < rules["min"] or f > rules["max"]:
                raise ValidationError(f"{name} out of range")
        elif value_type == "categorical":
            if value not in rules["choices"]:
                raise ValidationError(f"{name} invalid choice")
