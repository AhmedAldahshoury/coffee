from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.brew import BrewCreate, BrewListResponse, BrewRead
from coffee_backend.services.brew_service import BrewService

router = APIRouter(prefix="/brews", tags=["brews"])


@router.post("", response_model=BrewRead, status_code=status.HTTP_201_CREATED)
def create_brew(
    payload: BrewCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return BrewService(db).create_brew(user.id, payload)


@router.get("", response_model=list[BrewRead] | BrewListResponse)
def list_brews(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int | None, Query(ge=1)] = None,
    page_size: Annotated[int | None, Query(ge=1, le=100)] = None,
    include_total: bool = False,
    method: str | None = None,
    brewed_from: datetime | None = None,
    brewed_to: datetime | None = None,
    sort_by: Literal["date", "score"] = "date",
    sort_order: Literal["asc", "desc"] = "desc",
):
    service = BrewService(db)

    if (page is None) != (page_size is None):
        page = page or 1
        page_size = page_size or 20

    brews, total = service.list_brews(
        user.id,
        page=page,
        page_size=page_size,
        include_total=include_total,
        method=method,
        brewed_from=brewed_from,
        brewed_to=brewed_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    if page is None or page_size is None:
        return brews

    return BrewListResponse(items=brews, page=page, page_size=page_size, total=total)


@router.get("/{brew_id}", response_model=BrewRead)
def get_brew(
    brew_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return BrewService(db).get_brew(user.id, brew_id)
