from pydantic import BaseModel, Field


class CSVImportRequest(BaseModel):
    method: str | None = None
    data_path: str
    meta_path: str | None = None


class CSVImportError(BaseModel):
    row: int
    detail: str
    code: str
    fields: dict[str, str] | None = None


class CSVImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[CSVImportError] = Field(default_factory=list)


class CSVExportResult(BaseModel):
    output_files: list[str]
