import typer
import uvicorn

app = typer.Typer(help="API commands")


@app.command("run")
def run_api(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run("coffee_backend.main:app", host=host, port=port, reload=False)
