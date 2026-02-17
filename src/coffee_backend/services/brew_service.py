from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.core.exceptions import ValidationError
from coffee_backend.db.models.brew import Brew
from coffee_backend.schemas.brew import BrewCreate
from coffee_backend.services.parameter_validation import validate_method_parameters


class BrewService:
    def __init__(self, db: Session):
        self.db = db

    def create_brew(self, user_id: str, payload: BrewCreate, import_hash: str | None = None) -> Brew:
        validate_method_parameters(payload.method, payload.parameters)
        brew = Brew(user_id=user_id, **payload.model_dump(), import_hash=import_hash)
        self.db.add(brew)
        self.db.commit()
        self.db.refresh(brew)
        return brew

    def list_brews(self, user_id: str) -> list[Brew]:
        return list(self.db.scalars(select(Brew).where(Brew.user_id == user_id).order_by(Brew.brewed_at.desc())))

    def get_brew(self, user_id: str, brew_id: str) -> Brew:
        brew = self.db.scalar(select(Brew).where(Brew.user_id == user_id, Brew.id == brew_id))
        if brew is None:
            raise ValidationError("Brew not found")
        return brew
