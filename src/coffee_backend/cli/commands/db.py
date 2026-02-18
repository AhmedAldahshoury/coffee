import subprocess

import typer

app = typer.Typer(help="Database migration commands")


def _run_alembic(args: list[str]) -> None:
    subprocess.run(["alembic", *args], check=True)


@app.command("upgrade")
def upgrade(revision: str = "head") -> None:
    _run_alembic(["upgrade", revision])


@app.command("downgrade")
def downgrade(revision: str) -> None:
    _run_alembic(["downgrade", revision])


@app.command("revision")
def revision(message: str, autogenerate: bool = True) -> None:
    args = ["revision", "-m", message]
    if autogenerate:
        args.append("--autogenerate")
    _run_alembic(args)


@app.command("stamp")
def stamp(revision: str = "head") -> None:
    _run_alembic(["stamp", revision])


@app.command("migrate")
def migrate() -> None:
    _run_alembic(["upgrade", "head"])
