from uuid import UUID

import typer

from coffee_backend.cli.db import get_cli_db_session
from coffee_backend.schemas.optimisation import StudyRequest
from coffee_backend.services.optimisation_service import OptimisationService

app = typer.Typer(help="Optimisation commands")


@app.command("suggest")
def suggest(
    user_id: UUID,
    method_id: str,
    variant_id: str | None = None,
    bean_id: UUID | None = None,
    equipment_id: UUID | None = None,
) -> None:
    req = StudyRequest(
        method_id=method_id,
        variant_id=variant_id,
        bean_id=bean_id,
        equipment_id=equipment_id,
    )
    with get_cli_db_session() as db:
        s = OptimisationService(db).suggest(user_id, req)
        typer.echo(f"{s.id} {s.suggested_params}")


@app.command("apply")
def apply(
    user_id: UUID,
    suggestion_id: UUID,
    brew_id: UUID,
    score: float | None = None,
    failed: bool = False,
) -> None:
    with get_cli_db_session() as db:
        s = OptimisationService(db).apply(user_id, suggestion_id, brew_id, score, failed)
        typer.echo(f"Applied suggestion {s.id}")
