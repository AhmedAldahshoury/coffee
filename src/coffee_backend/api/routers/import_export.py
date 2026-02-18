import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from coffee_backend.api.deps import get_current_user
from coffee_backend.db.models.user import User
from coffee_backend.db.session import get_db
from coffee_backend.schemas.import_export import CSVImportRequest, CSVImportResult
from coffee_backend.services.import_export_service import ImportExportService

router = APIRouter(prefix="", tags=["import-export"])
logger = logging.getLogger(__name__)


@router.post("/import/csv", response_model=CSVImportResult)
def import_csv(
    payload: CSVImportRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CSVImportResult:
    logger.info(
        "import.csv.requested",
        extra={"user_id": str(user.id), "data_path": payload.data_path},
    )
    result = ImportExportService(db).import_csv(user.id, payload)
    logger.info(
        "import.csv.completed",
        extra={
            "user_id": str(user.id),
            "processed": result.processed,
            "inserted": result.inserted,
            "skipped": result.skipped,
            "error_count": result.error_count,
        },
    )
    return result


@router.get("/export/csv")
def export_csv(
    out_dir: Annotated[str, Query()],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, list[str]]:
    logger.info("export.csv.requested", extra={"user_id": str(user.id), "out_dir": out_dir})
    result = ImportExportService(db).export_csv(user.id, out_dir)
    return {"output_files": result.output_files}
