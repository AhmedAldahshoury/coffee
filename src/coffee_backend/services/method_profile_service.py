from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from coffee_backend.core.exceptions import NotFoundError
from coffee_backend.db.models.method_profile import MethodProfile

MethodProfilePayload = dict[str, object]

INITIAL_METHOD_PROFILES: list[MethodProfilePayload] = [
    {
        "method_id": "v60",
        "variant_id": "v60_default",
        "schema_version": 1,
        "parameters": [
            {
                "name": "dose_g",
                "type": "float",
                "min": 12.0,
                "max": 20.0,
                "step": 0.5,
                "unit": "g",
                "default": 15.0,
                "description": "Coffee dose used for brewing.",
            },
            {
                "name": "ratio",
                "type": "float",
                "min": 15.0,
                "max": 18.5,
                "step": 0.1,
                "unit": ":1",
                "default": 16.5,
                "description": "Coffee-to-water ratio.",
            },
            {
                "name": "grind_step",
                "type": "int",
                "min": 1,
                "max": 40,
                "step": 1,
                "unit": "steps",
                "default": 20,
                "description": "Generic grinder step setting.",
            },
            {
                "name": "temp_c",
                "type": "int",
                "min": 88,
                "max": 96,
                "step": 1,
                "unit": "°C",
                "default": 92,
                "description": "Brewing water temperature.",
            },
            {
                "name": "total_time_s",
                "type": "int",
                "min": 150,
                "max": 240,
                "step": 5,
                "unit": "s",
                "default": 190,
                "description": "Total brew time.",
            },
            {
                "name": "bloom_ratio",
                "type": "float",
                "min": 2.0,
                "max": 3.0,
                "step": 0.1,
                "unit": "x dose",
                "default": 2.5,
                "description": "Bloom water multiplier of coffee dose.",
            },
            {
                "name": "bloom_s",
                "type": "int",
                "min": 25,
                "max": 50,
                "step": 5,
                "unit": "s",
                "default": 30,
                "description": "Bloom duration.",
            },
            {
                "name": "pours",
                "type": "int",
                "min": 2,
                "max": 5,
                "step": 1,
                "unit": "count",
                "default": 3,
                "description": "Number of pours after bloom.",
            },
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_standard",
        "schema_version": 1,
        "parameters": [
            {
                "name": "dose_g",
                "type": "float",
                "min": 12.0,
                "max": 20.0,
                "step": 0.5,
                "unit": "g",
                "default": 15.0,
                "description": "Coffee dose used for brewing.",
            },
            {
                "name": "water_g",
                "type": "int",
                "min": 150,
                "max": 280,
                "step": 5,
                "unit": "g",
                "default": 230,
                "description": "Total brewing water mass.",
            },
            {
                "name": "grind_step",
                "type": "int",
                "min": 1,
                "max": 40,
                "step": 1,
                "unit": "steps",
                "default": 18,
                "description": "Generic grinder step setting.",
            },
            {
                "name": "temp_c",
                "type": "int",
                "min": 75,
                "max": 95,
                "step": 1,
                "unit": "°C",
                "default": 85,
                "description": "Brewing water temperature.",
            },
            {
                "name": "steep_s",
                "type": "int",
                "min": 30,
                "max": 150,
                "step": 5,
                "unit": "s",
                "default": 60,
                "description": "Steeping duration before plunging.",
            },
            {
                "name": "plunge_s",
                "type": "int",
                "min": 15,
                "max": 45,
                "step": 5,
                "unit": "s",
                "default": 25,
                "description": "Plunge duration.",
            },
            {
                "name": "stir_count",
                "type": "int",
                "min": 0,
                "max": 20,
                "step": 1,
                "unit": "count",
                "default": 5,
                "description": "Number of stirs during agitation.",
            },
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_inverted",
        "schema_version": 1,
        "parameters": [
            {
                "name": "dose_g",
                "type": "float",
                "min": 12.0,
                "max": 20.0,
                "step": 0.5,
                "unit": "g",
                "default": 15.0,
                "description": "Coffee dose used for brewing.",
            },
            {
                "name": "water_g",
                "type": "int",
                "min": 150,
                "max": 280,
                "step": 5,
                "unit": "g",
                "default": 230,
                "description": "Total brewing water mass.",
            },
            {
                "name": "grind_step",
                "type": "int",
                "min": 1,
                "max": 40,
                "step": 1,
                "unit": "steps",
                "default": 18,
                "description": "Generic grinder step setting.",
            },
            {
                "name": "temp_c",
                "type": "int",
                "min": 75,
                "max": 95,
                "step": 1,
                "unit": "°C",
                "default": 85,
                "description": "Brewing water temperature.",
            },
            {
                "name": "steep_s",
                "type": "int",
                "min": 30,
                "max": 150,
                "step": 5,
                "unit": "s",
                "default": 90,
                "description": "Steeping duration before plunging.",
            },
            {
                "name": "plunge_s",
                "type": "int",
                "min": 15,
                "max": 45,
                "step": 5,
                "unit": "s",
                "default": 25,
                "description": "Plunge duration.",
            },
            {
                "name": "stir_count",
                "type": "int",
                "min": 0,
                "max": 20,
                "step": 1,
                "unit": "count",
                "default": 8,
                "description": "Number of stirs during agitation.",
            },
        ],
    },
]


class MethodProfileService:
    def __init__(self, db: Session):
        self.db = db

    def list_profiles(self) -> list[MethodProfile]:
        query: Select[tuple[MethodProfile]] = select(MethodProfile).order_by(
            MethodProfile.method_id,
            MethodProfile.variant_id,
            MethodProfile.schema_version.desc(),
        )
        return list(self.db.scalars(query))

    def list_profiles_for_method(self, method_id: str) -> list[MethodProfile]:
        query: Select[tuple[MethodProfile]] = (
            select(MethodProfile)
            .where(MethodProfile.method_id == method_id)
            .order_by(MethodProfile.variant_id, MethodProfile.schema_version.desc())
        )
        profiles = list(self.db.scalars(query))
        if not profiles:
            raise NotFoundError(f"Method '{method_id}' was not found")
        return profiles

    def get_profile(self, method_id: str, variant_id: str) -> MethodProfile:
        query: Select[tuple[MethodProfile]] = (
            select(MethodProfile)
            .where(MethodProfile.method_id == method_id)
            .where(MethodProfile.variant_id == variant_id)
            .order_by(MethodProfile.schema_version.desc())
        )
        profile = self.db.scalars(query).first()
        if profile is None:
            raise NotFoundError(f"Method variant '{method_id}/{variant_id}' was not found")
        return profile


def seed_method_profiles(db: Session) -> None:
    existing = db.scalar(select(MethodProfile.method_id).limit(1))
    if existing is not None:
        return

    for payload in INITIAL_METHOD_PROFILES:
        db.add(MethodProfile(**payload))

    db.commit()
