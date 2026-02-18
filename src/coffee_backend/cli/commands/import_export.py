from uuid import UUID

import typer

from coffee_backend.db.session import SessionLocal
from coffee_backend.schemas.import_export import CSVImportRequest
from coffee_backend.services.import_export_service import ImportExportService

app = typer.Typer(help="Import commands")
export_app = typer.Typer(help="Export commands")


@app.command("csv")
def import_csv(
    user_id: UUID, data: str, method: str | None = None, meta: str | None = None
) -> None:
    with SessionLocal() as db:
        result = ImportExportService(db).import_csv(
            user_id, CSVImportRequest(method=method, data_path=data, meta_path=meta)
        )
        typer.echo(f"Imported={result.imported} skipped={result.skipped}")


@export_app.command("csv")
def export_csv(user_id: UUID, out: str) -> None:
    with SessionLocal() as db:
        result = ImportExportService(db).export_csv(user_id, out)
        typer.echo("\n".join(result.output_files))
