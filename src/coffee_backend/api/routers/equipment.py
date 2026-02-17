from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.equipment import Equipment
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.equipment import EquipmentCreate, EquipmentRead

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.post("", response_model=EquipmentRead)
def create_equipment(
    payload: EquipmentCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Equipment:
    row = Equipment(user_id=user.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[EquipmentRead])
def list_equipment(
    user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> list[Equipment]:
    return list(db.scalars(select(Equipment).where(Equipment.user_id == user.id)))
