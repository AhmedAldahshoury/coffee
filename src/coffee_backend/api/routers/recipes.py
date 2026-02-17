from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
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


@router.get("", response_model=list[RecipeRead])
def list_recipes(
    user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> list[Recipe]:
    return list(db.scalars(select(Recipe).where(Recipe.user_id == user.id)))
