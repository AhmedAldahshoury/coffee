import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.core.exceptions import ValidationError
from coffee_backend.db.models.recipe import Recipe
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.recipe import RecipeCreate, RecipeRead, RecipeRenderResponse, RecipeStep

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("", response_model=RecipeRead)
def create_recipe(
    payload: RecipeCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Recipe:
    row = Recipe(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[RecipeRead] | dict[str, object])
def list_recipes(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int | None, Query(ge=1)] = None,
    page_size: Annotated[int | None, Query(ge=1, le=100)] = None,
    include_total: bool = False,
) -> list[Recipe] | dict[str, object]:
    query = select(Recipe).where(Recipe.user_id == user.id)

    if (page is None) != (page_size is None):
        page = page or 1
        page_size = page_size or 20

    total = None
    if include_total:
        total = (
            db.scalar(select(func.count()).select_from(Recipe).where(Recipe.user_id == user.id))
            or 0
        )

    if page is not None and page_size is not None:
        query = query.offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(query))
        return {"items": items, "page": page, "page_size": page_size, "total": total}

    return list(db.scalars(query))


def _parse_recipe_params(raw: str | None, query_params: list[str] | None) -> dict[str, object]:
    if raw:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValidationError("params must be a JSON object", code="invalid_params")
        return parsed

    values: dict[str, object] = {}
    for entry in query_params or []:
        if "=" not in entry:
            raise ValidationError("Each param entry must be key=value", code="invalid_params")
        key, value = entry.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValidationError("Param key cannot be empty", code="invalid_params")
        try:
            values[key] = int(value)
        except ValueError:
            try:
                values[key] = float(value)
            except ValueError:
                values[key] = value
    return values


def _render_v60(variant_id: str, params: dict[str, object]) -> RecipeRenderResponse:
    dose = float(params.get("dose_g", 15.0))
    ratio = float(params.get("ratio", 16.5))
    bloom_ratio = float(params.get("bloom_ratio", 2.5))
    bloom_s = int(params.get("bloom_s", 30))
    pours = int(params.get("pours", 3))
    total_time = int(params.get("total_time_s", 190))

    total_water = round(dose * ratio)
    bloom_water = round(dose * bloom_ratio)
    remaining_water = max(0, total_water - bloom_water)
    per_pour = round(remaining_water / max(pours, 1))
    pulse_window = max(total_time - bloom_s, 0)
    pulse_gap = pulse_window // max(pours, 1)

    steps: list[RecipeStep] = [
        RecipeStep(
            text=f"Bloom: pour {bloom_water}g water and wait {bloom_s}s.",
            timer_seconds=bloom_s,
        )
    ]
    for i in range(1, pours + 1):
        target = bloom_water + (per_pour * i)
        seconds = bloom_s + (pulse_gap * i)
        steps.append(
            RecipeStep(
                text=f"Pour pulse {i}: add water to ~{target}g total by {seconds}s.",
                timer_seconds=pulse_gap if pulse_gap > 0 else None,
            )
        )

    return RecipeRenderResponse(
        title=f"V60 ({variant_id})",
        equipment=["V60 dripper", "Filter", "Gooseneck kettle", "Scale", "Timer"],
        steps=steps,
    )


def _render_aeropress(variant_id: str, params: dict[str, object]) -> RecipeRenderResponse:
    water = int(params.get("water_g", 230))
    stir = int(params.get("stir_count", 5))
    steep = int(params.get("steep_s", 60))
    plunge = int(params.get("plunge_s", 25))

    return RecipeRenderResponse(
        title=f"Aeropress ({variant_id})",
        equipment=["Aeropress", "Filter", "Kettle", "Scale", "Stirrer", "Timer"],
        steps=[
            RecipeStep(text=f"Add {water}g water to the chamber."),
            RecipeStep(text=f"Stir {stir} times to evenly saturate grounds."),
            RecipeStep(text=f"Steep for {steep}s.", timer_seconds=steep),
            RecipeStep(text=f"Plunge gently for {plunge}s.", timer_seconds=plunge),
        ],
    )


@router.get("/render", response_model=RecipeRenderResponse)
def render_recipe(
    method_id: Annotated[str, Query()],
    variant_id: Annotated[str, Query()],
    params: Annotated[
        str | None,
        Query(
            description="JSON object string of recipe params",
            examples=[
                '{"dose_g":15,"ratio":16.5,"bloom_ratio":2.5,"bloom_s":30,"pours":3,"total_time_s":180}'
            ],
        ),
    ] = None,
    param: Annotated[
        list[str] | None,
        Query(description="Repeatable key=value params", examples=["water_g=220", "steep_s=75"]),
    ] = None,
) -> RecipeRenderResponse:
    parsed_params = _parse_recipe_params(params, param)
    method = method_id.strip().lower()

    if method == "v60":
        return _render_v60(variant_id, parsed_params)
    if method == "aeropress":
        return _render_aeropress(variant_id, parsed_params)

    raise ValidationError("Unsupported method for recipe rendering", code="unsupported_method")
