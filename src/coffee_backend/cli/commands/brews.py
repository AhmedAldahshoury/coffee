from datetime import datetime
from uuid import UUID

import typer

from coffee_backend.cli.db import get_cli_db_session
from coffee_backend.schemas.brew import BrewCreate
from coffee_backend.services.brew_service import BrewService

app = typer.Typer(help="Brew commands")


@app.command("add")
def add_brew(
    user_id: UUID = typer.Option(..., "--user-id", help="Owner user id"),
    method: str = typer.Option(..., "--method", help="Brew method, e.g. aeropress"),
    brewed_at: str = typer.Option(..., "--brewed-at", help="ISO timestamp"),
    parameters_json: str = typer.Option(
        ..., "--parameters-json", help="JSON object of brew parameters"
    ),
    score: float | None = typer.Option(None, "--score", help="Optional brew score"),
    failed: bool = typer.Option(False, "--failed", help="Mark brew as failed"),
    comments: str = typer.Option("", "--comments", help="Optional comments"),
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
    with get_cli_db_session() as db:
        brew = BrewService(db).create_brew(user_id, payload)
        typer.echo(f"Created brew {brew.id}")


@app.command("list")
def list_brews(user_id: UUID = typer.Option(..., "--user-id", help="Owner user id")) -> None:
    with get_cli_db_session() as db:
        for brew in BrewService(db).list_brews(user_id):
            typer.echo(f"{brew.id} {brew.method} score={brew.score}")


@app.command("show")
def show_brew(
    user_id: UUID = typer.Option(..., "--user-id", help="Owner user id"),
    brew_id: UUID = typer.Option(..., "--brew-id", help="Brew id"),
) -> None:
    with get_cli_db_session() as db:
        brew = BrewService(db).get_brew(user_id, brew_id)
        typer.echo(f"{brew.id} {brew.parameters}")
