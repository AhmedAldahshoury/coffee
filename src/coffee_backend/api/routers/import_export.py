from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.core.exceptions import ValidationError
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.import_export import CSVImportRequest, CSVImportResult
from coffee_backend.services.import_export_service import ImportExportService

router = APIRouter(prefix="", tags=["import-export"])


@router.post("/import/csv", response_model=CSVImportResult)
def import_csv(
    payload: CSVImportRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CSVImportResult:
    try:
        return ImportExportService(db).import_csv(user.id, payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/export/csv")
def export_csv(
    out_dir: Annotated[str, Query()],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, list[str]]:
    result = ImportExportService(db).export_csv(user.id, out_dir)
    return {"output_files": result.output_files}
