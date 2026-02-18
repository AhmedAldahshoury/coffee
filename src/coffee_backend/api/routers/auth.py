import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.core.security import create_access_token
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.user import TokenResponse, UserCreate, UserLogin, UserRead
from coffee_backend.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    service = UserService(db)
    user = service.create_user(payload)
    logger.info("auth.register.success", extra={"user_id": str(user.id), "email": user.email})
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    service = UserService(db)
    user = service.authenticate(payload.email, payload.password)
    if user is None:
        logger.warning("auth.login.failed", extra={"email": payload.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    logger.info("auth.login.success", extra={"user_id": str(user.id), "email": user.email})
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
