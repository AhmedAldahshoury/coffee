from coffee_backend.core.exceptions import ValidationError
from coffee_backend.schemas.parameter_registry import METHOD_PARAMETER_REGISTRY


def validate_method_parameters(
    method: str,
    params: dict[str, object],
    *,
    allow_unknown: bool = False,
) -> None:
    schema = METHOD_PARAMETER_REGISTRY.get(method)
    if schema is None:
        raise ValidationError(f"Unsupported method: {method}", code="unsupported_method")

    unknown_keys = sorted(key for key in params if key not in schema)
    if unknown_keys and not allow_unknown:
        raise ValidationError(
            "Unknown parameter keys",
            code="unknown_parameter_keys",
            fields=dict.fromkeys(unknown_keys, "unknown parameter"),
        )

    missing_required = sorted(
        name for name, rules in schema.items() if rules.get("required") and name not in params
    )
    if missing_required:
        raise ValidationError(
            "Missing required parameters",
            code="missing_required_parameters",
            fields=dict.fromkeys(missing_required, "required parameter missing"),
        )

    for name, value in params.items():
        if name not in schema:
            continue
        rules = schema[name]
        value_type = rules["type"]

        if value_type == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValidationError(
                    f"{name} must be int",
                    code="invalid_parameter_type",
                    fields={name: "must be int"},
                )
            if value < rules["min"] or value > rules["max"]:
                raise ValidationError(
                    f"{name} out of range",
                    code="parameter_out_of_range",
                    fields={name: f"must be between {rules['min']} and {rules['max']}"},
                )

        elif value_type == "float":
            if not isinstance(value, (float, int)) or isinstance(value, bool):
                raise ValidationError(
                    f"{name} must be number",
                    code="invalid_parameter_type",
                    fields={name: "must be number"},
                )
            numeric_value = float(value)
            if numeric_value < rules["min"] or numeric_value > rules["max"]:
                raise ValidationError(
                    f"{name} out of range",
                    code="parameter_out_of_range",
                    fields={name: f"must be between {rules['min']} and {rules['max']}"},
                )

        elif value_type == "categorical":
            if value not in rules["choices"]:
                raise ValidationError(
                    f"{name} invalid choice",
                    code="invalid_parameter_choice",
                    fields={name: f"must be one of {rules['choices']}"},
                )
