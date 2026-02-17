from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
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


@router.get("", response_model=list[BeanRead])
def list_beans(
    user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> list[Bean]:
    return list(db.scalars(select(Bean).where(Bean.user_id == user.id)))
