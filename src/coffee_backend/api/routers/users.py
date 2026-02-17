from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.user import UserRead
from coffee_backend.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    _: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
) -> list[User]:
    return UserService(db).list_users()
