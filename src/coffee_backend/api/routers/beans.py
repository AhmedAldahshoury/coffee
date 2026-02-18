from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.bean import Bean
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.bean import BeanCreate, BeanRead

router = APIRouter(prefix="/beans", tags=["beans"])


@router.post("", response_model=BeanRead)
def create_bean(
    payload: BeanCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Bean:
    bean = Bean(user_id=user.id, **payload.model_dump())
    db.add(bean)
    db.commit()
    db.refresh(bean)
    return bean


@router.get("", response_model=list[BeanRead] | dict[str, object])
def list_beans(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int | None, Query(ge=1)] = None,
    page_size: Annotated[int | None, Query(ge=1, le=100)] = None,
    include_total: bool = False,
) -> list[Bean] | dict[str, object]:
    query = select(Bean).where(Bean.user_id == user.id)

    if (page is None) != (page_size is None):
        page = page or 1
        page_size = page_size or 20

    total = None
    if include_total:
        total = db.scalar(
            select(func.count()).select_from(Bean).where(Bean.user_id == user.id)
        ) or 0

    if page is not None and page_size is not None:
        query = query.offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(query))
        return {"items": items, "page": page, "page_size": page_size, "total": total}

    return list(db.scalars(query))
