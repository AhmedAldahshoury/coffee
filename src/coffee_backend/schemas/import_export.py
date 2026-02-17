from pydantic import BaseModel


class CSVImportRequest(BaseModel):
    method: str | None = None
    data_path: str
    meta_path: str | None = None


class CSVImportResult(BaseModel):
    imported: int
    skipped: int


class CSVExportResult(BaseModel):
    output_files: list[str]
