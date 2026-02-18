from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from coffee_backend.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ready", "db": "ok"}
