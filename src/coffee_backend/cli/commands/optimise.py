from uuid import UUID

import typer

from coffee_backend.db.session import SessionLocal
from coffee_backend.schemas.optimisation import StudyRequest
from coffee_backend.services.optimisation_service import OptimisationService

app = typer.Typer(help="Optimisation commands")


@app.command("suggest")
def suggest(
    user_id: UUID,
    method: str,
    bean_id: UUID | None = None,
    equipment_id: UUID | None = None,
    recipe_id: UUID | None = None,
) -> None:
    req = StudyRequest(
        method=method, bean_id=bean_id, equipment_id=equipment_id, recipe_id=recipe_id
    )
    with SessionLocal() as db:
        s = OptimisationService(db).suggest(user_id, req)
        typer.echo(f"{s.id} {s.suggested_parameters}")


@app.command("apply")
def apply(
    user_id: UUID,
    suggestion_id: UUID,
    brew_id: UUID,
    score: float | None = None,
    failed: bool = False,
) -> None:
    with SessionLocal() as db:
        s = OptimisationService(db).apply(user_id, suggestion_id, brew_id, score, failed)
        typer.echo(f"Applied suggestion {s.id}")
