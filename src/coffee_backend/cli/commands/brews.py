from datetime import datetime
from uuid import UUID

import typer

from coffee_backend.db.session import SessionLocal
from coffee_backend.schemas.brew import BrewCreate
from coffee_backend.services.brew_service import BrewService

app = typer.Typer(help="Brew commands")


@app.command("add")
def add_brew(
    user_id: UUID,
    method: str,
    brewed_at: str,
    parameters_json: str,
    score: float | None = None,
    failed: bool = False,
    comments: str = "",
) -> None:
    import json

    payload = BrewCreate(
        method=method,
        brewed_at=datetime.fromisoformat(brewed_at),
        parameters=json.loads(parameters_json),
        score=score,
        failed=failed,
        comments=comments or None,
    )
    with SessionLocal() as db:
        brew = BrewService(db).create_brew(user_id, payload)
        typer.echo(f"Created brew {brew.id}")


@app.command("list")
def list_brews(user_id: UUID) -> None:
    with SessionLocal() as db:
        for brew in BrewService(db).list_brews(user_id):
            typer.echo(f"{brew.id} {brew.method} score={brew.score}")


@app.command("show")
def show_brew(user_id: UUID, brew_id: UUID) -> None:
    with SessionLocal() as db:
        brew = BrewService(db).get_brew(user_id, brew_id)
        typer.echo(f"{brew.id} {brew.parameters}")
