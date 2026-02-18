import typer

from coffee_backend.cli.db import get_cli_db_session
from coffee_backend.schemas.user import UserCreate
from coffee_backend.services.user_service import UserService

app = typer.Typer(help="User commands")


@app.command("create")
def create_user(
    email: str = typer.Option(..., "--email", help="User email"),
    password: str = typer.Option(..., "--password", help="User password"),
    name: str = typer.Option("", "--name", help="Optional display name"),
) -> None:
    with get_cli_db_session() as db:
        user = UserService(db).create_user(
            UserCreate(email=email, password=password, name=name or None)
        )
        typer.echo(f"Created user {user.id} ({user.email})")


@app.command("list")
def list_users() -> None:
    with get_cli_db_session() as db:
        for user in UserService(db).list_users():
            typer.echo(f"{user.id} {user.email} {user.name or ''}")
