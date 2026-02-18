from typing import Literal

from pydantic import BaseModel, Field


class DependsOnSchema(BaseModel):
    name: str = Field(description="Stable key of the controlling parameter.")
    value: int | float | bool | str = Field(
        description="Expected value of the controlling parameter for this parameter to apply."
    )


class MethodParameterDefinition(BaseModel):
    name: str = Field(description="Stable parameter key.")
    type: Literal["int", "float", "bool", "enum"] = Field(description="Parameter data type.")
    min: int | float | None = Field(
        default=None,
        description="Inclusive lower bound for numeric values.",
    )
    max: int | float | None = Field(
        default=None,
        description="Inclusive upper bound for numeric values.",
    )
    step: int | float | None = Field(
        default=None,
        description="Increment step for numeric values.",
    )
    unit: str | None = Field(default=None, description="Display unit for the parameter.")
    default: int | float | bool | str = Field(description="Default parameter value.")
    description: str = Field(description="Short description of the parameter in British English.")
    depends_on: DependsOnSchema | None = Field(
        default=None,
        description="Optional condition describing when this parameter is relevant.",
    )


class MethodProfileSchema(BaseModel):
    method_id: str = Field(description="Brew method identifier.")
    variant_id: str | None = Field(
        default=None,
        description="Optional method profile variant identifier.",
    )
    schema_version: int = Field(description="Schema version number.")
    parameters: list[MethodParameterDefinition] = Field(
        description="Parameter definitions for this brew method profile."
    )


class MethodVariantSummary(BaseModel):
    variant_id: str | None = Field(
        default=None,
        description="Optional method profile variant identifier.",
    )
    schema_version: int = Field(description="Latest schema version for this variant.")


class MethodSummary(BaseModel):
    method_id: str = Field(description="Brew method identifier.")
    variants: list[MethodVariantSummary] = Field(
        description="Available variants and their latest schema versions."
    )


class MethodSummaryListResponse(BaseModel):
    methods: list[MethodSummary]


class MethodProfileListResponse(BaseModel):
    method_id: str
    profiles: list[MethodProfileSchema]
