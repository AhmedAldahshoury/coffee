from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.brew import BrewCreate, BrewRead
from coffee_backend.services.brew_service import BrewService

router = APIRouter(prefix="/brews", tags=["brews"])


@router.post("", response_model=BrewRead, status_code=status.HTTP_201_CREATED)
def create_brew(
    payload: BrewCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return BrewService(db).create_brew(user.id, payload)


@router.get("", response_model=list[BrewRead])
def list_brews(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return BrewService(db).list_brews(user.id)


@router.get("/{brew_id}", response_model=BrewRead)
def get_brew(
    brew_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return BrewService(db).get_brew(user.id, brew_id)
