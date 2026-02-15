from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.persistence import Brew, User
from app.schemas.brew import BrewCreateRequest

router = APIRouter(prefix="/brews", tags=["Brews"])


@router.post("")
def submit_brew(
    payload: BrewCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    brew = Brew(user_id=user.id, **payload.model_dump())
    db.add(brew)
    db.commit()
    db.refresh(brew)
    return {"id": brew.id, "score": brew.score}
