from dataclasses import dataclass


@dataclass(frozen=True)
class OptimizationContext:
    dataset_prefix: str
    method: str
    persons: list[str] | None
    best_only: bool
    prior_weight: float
