from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from coffee_backend.db.session import get_db
from coffee_backend.schemas.method_profile import (
    MethodProfileListResponse,
    MethodProfileSchema,
    MethodSummary,
    MethodSummaryListResponse,
    MethodVariantSummary,
)
from coffee_backend.services.method_profile_service import MethodProfileService

router = APIRouter(prefix="/methods", tags=["methods"])


@router.get("", response_model=MethodSummaryListResponse)
def list_methods(db: Annotated[Session, Depends(get_db)]) -> MethodSummaryListResponse:
    profiles = MethodProfileService(db).list_profiles()
    grouped: dict[str, list[MethodVariantSummary]] = defaultdict(list)

    for profile in profiles:
        grouped[profile.method_id].append(
            MethodVariantSummary(
                variant_id=profile.variant_id,
                schema_version=profile.schema_version,
            )
        )

    summaries = [
        MethodSummary(method_id=method_id, variants=variants)
        for method_id, variants in grouped.items()
    ]
    return MethodSummaryListResponse(methods=summaries)


@router.get("/{method_id}", response_model=MethodProfileListResponse)
def get_method_profiles(
    method_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> MethodProfileListResponse:
    profiles = MethodProfileService(db).list_profiles_for_method(method_id)
    return MethodProfileListResponse(
        method_id=method_id,
        profiles=[
            MethodProfileSchema(
                method_id=profile.method_id,
                variant_id=profile.variant_id,
                schema_version=profile.schema_version,
                parameters=profile.parameters,
            )
            for profile in profiles
        ],
    )


@router.get("/{method_id}/{variant_id}", response_model=MethodProfileSchema)
def get_method_profile_variant(
    method_id: str,
    variant_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> MethodProfileSchema:
    profile = MethodProfileService(db).get_profile(method_id, variant_id)
    return MethodProfileSchema(
        method_id=profile.method_id,
        variant_id=profile.variant_id,
        schema_version=profile.schema_version,
        parameters=profile.parameters,
    )
