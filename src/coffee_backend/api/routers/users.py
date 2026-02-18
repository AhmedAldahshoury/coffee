from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.user import UserRead
from coffee_backend.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead] | dict[str, object])
def list_users(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int | None, Query(ge=1)] = None,
    page_size: Annotated[int | None, Query(ge=1, le=100)] = None,
    include_total: bool = False,
) -> list[User] | dict[str, object]:
    items = UserService(db).list_users()

    if (page is None) != (page_size is None):
        page = page or 1
        page_size = page_size or 20

    total = len(items) if include_total else None

    if page is not None and page_size is not None:
        start = (page - 1) * page_size
        end = start + page_size
        return {"items": items[start:end], "page": page, "page_size": page_size, "total": total}

    return items
