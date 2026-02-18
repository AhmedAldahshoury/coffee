from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from coffee_backend.api.routers import (
    analytics,
    auth,
    beans,
    brews,
    equipment,
    health,
    import_export,
    optimisation,
    recipes,
    users,
)
from coffee_backend.core.config import Settings
from coffee_backend.core.logging import configure_logging
from coffee_backend.db.session import dispose_db_state, init_db_state

configure_logging()


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        init_db_state(app.state, settings=settings)
        try:
            yield
        finally:
            dispose_db_state(app.state)

    app = FastAPI(
        title="Coffee Optimiser Backend",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(beans.router, prefix="/api/v1")
    app.include_router(equipment.router, prefix="/api/v1")
    app.include_router(recipes.router, prefix="/api/v1")
    app.include_router(brews.router, prefix="/api/v1")
    app.include_router(optimisation.router, prefix="/api/v1")
    app.include_router(import_export.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    return app


app = create_app()
