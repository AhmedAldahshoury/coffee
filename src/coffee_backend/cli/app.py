import typer

from coffee_backend.cli.commands import brews, db, import_export, optimise, run, users

app = typer.Typer(help="Coffee Optimiser CLI")
app.add_typer(run.app, name="api")
app.add_typer(db.app, name="db")
app.add_typer(users.app, name="user")
app.add_typer(brews.app, name="brew")
app.add_typer(optimise.app, name="optimise")
app.add_typer(import_export.app, name="import")
app.add_typer(import_export.export_app, name="export")

if __name__ == "__main__":
    app()
