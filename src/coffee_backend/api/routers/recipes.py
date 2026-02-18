from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.recipe import Recipe
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.recipe import RecipeCreate, RecipeRead

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
        total = db.scalar(
            select(func.count()).select_from(Recipe).where(Recipe.user_id == user.id)
        ) or 0

    if page is not None and page_size is not None:
        query = query.offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(query))
        return {"items": items, "page": page, "page_size": page_size, "total": total}

    return list(db.scalars(query))
