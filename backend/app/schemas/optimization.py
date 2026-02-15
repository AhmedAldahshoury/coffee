from pydantic import BaseModel, Field, field_validator


class OptimizationRequest(BaseModel):
    dataset_prefix: str = Field(..., description="Dataset prefix to load <prefix>data.csv and <prefix>meta.csv")
    method: str = Field(default="median")
    persons: list[str] | None = None
    best_only: bool = Field(default=False)
    prior_weight: float = Field(default=0.666, gt=0)

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        valid = {"mean", "median", "lowest", "highest"}
        if value not in valid:
            raise ValueError(f"method must be one of {sorted(valid)}")
        return value


class SuggestedParameter(BaseModel):
    name: str
    value: str | float | int
    unit: str | None = None
    fixed: bool = False


class OptimizationResponse(BaseModel):
    score: float | None
    suggested_parameters: list[SuggestedParameter]
