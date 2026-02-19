import logging
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.background import BackgroundTask
from fastapi.responses import FileResponse
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


@router.post("/import/csv/upload", response_model=CSVImportResult)
def import_csv_upload(
    file: Annotated[UploadFile, File(...)],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    method: Annotated[str | None, Form()] = None,
) -> CSVImportResult:
    suffix = Path(file.filename or "upload.csv").suffix or ".csv"
    with NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        contents = file.file.read()
        handle.write(contents)
        temp_path = Path(handle.name)

    try:
        logger.info(
            "import.csv.upload.requested",
            extra={"user_id": str(user.id), "filename": file.filename},
        )
        result = ImportExportService(db).import_csv(
            user.id,
            CSVImportRequest(method=method, data_path=str(temp_path)),
        )
        return result
    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/export/csv")
def export_csv(
    out_dir: Annotated[str, Query()],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, list[str]]:
    logger.info("export.csv.requested", extra={"user_id": str(user.id), "out_dir": out_dir})
    result = ImportExportService(db).export_csv(user.id, out_dir)
    return {"output_files": result.output_files}


@router.get("/export/csv/download")
def export_csv_download(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    temp_dir = TemporaryDirectory()
    result = ImportExportService(db).export_csv(user.id, temp_dir.name)
    path = Path(result.output_files[0])
    response = FileResponse(path, media_type="text/csv", filename="brews.export.csv")
    response.background = BackgroundTask(temp_dir.cleanup)
    return response
