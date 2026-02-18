from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from coffee_backend.core.exceptions import NotFoundError
from coffee_backend.db.models.brew import Brew
from coffee_backend.db.models.method_profile import MethodProfile
from coffee_backend.schemas.brew import BrewCreate
from coffee_backend.services.parameter_validation import validate_method_parameters


class BrewService:
    def __init__(self, db: Session):
        self.db = db

    def _resolve_variant_id(self, method_id: str, variant_id: str | None) -> str:
        if variant_id is not None:
            return variant_id

        profiles = list(
            self.db.scalars(
                select(MethodProfile)
                .where(MethodProfile.method_id == method_id)
                .order_by(MethodProfile.variant_id.asc(), MethodProfile.schema_version.desc())
            )
        )
        if not profiles:
            return f"{method_id}_default"

        default_variant = next((p.variant_id for p in profiles if "default" in p.variant_id), None)
        return default_variant or profiles[0].variant_id

    def create_brew(
        self, user_id: str, payload: BrewCreate, import_hash: str | None = None
    ) -> Brew:
        validate_method_parameters(payload.method, payload.parameters)
        brew_payload = payload.model_dump()
        brew_payload["variant_id"] = self._resolve_variant_id(payload.method, payload.variant_id)
        brew = Brew(user_id=user_id, **brew_payload, import_hash=import_hash)
        self.db.add(brew)
        self.db.commit()
        self.db.refresh(brew)
        return brew

    def list_brews(
        self,
        user_id: str,
        page: int | None = None,
        page_size: int | None = None,
        include_total: bool = False,
        method: str | None = None,
        brewed_from: datetime | None = None,
        brewed_to: datetime | None = None,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> tuple[list[Brew], int | None]:
        filters = [Brew.user_id == user_id]
        if method is not None:
            filters.append(Brew.method == method)
        if brewed_from is not None:
            filters.append(Brew.brewed_at >= brewed_from)
        if brewed_to is not None:
            filters.append(Brew.brewed_at <= brewed_to)

        sort_column = Brew.brewed_at if sort_by == "date" else Brew.score
        order_clause = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        query = select(Brew).where(*filters).order_by(order_clause, Brew.created_at.desc())

        total: int | None = None
        if include_total:
            total = self.db.scalar(select(func.count()).select_from(Brew).where(*filters)) or 0

        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

        return list(self.db.scalars(query)), total

    def get_brew(self, user_id: str, brew_id: str) -> Brew:
        brew = self.db.scalar(select(Brew).where(Brew.id == brew_id, Brew.user_id == user_id))
        if brew is None:
            raise NotFoundError("Brew not found", code="brew_not_found")
        return brew
