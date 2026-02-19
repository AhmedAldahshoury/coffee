import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError

from coffee_backend.api.routers import (
    analytics,
    auth,
    beans,
    brews,
    equipment,
    health,
    import_export,
    methods,
    optimisation,
    recipes,
    users,
)
from coffee_backend.core.config import Settings, get_settings
from coffee_backend.core.exceptions import APIError, ConflictError
from coffee_backend.core.logging import configure_logging, request_id_ctx_var
from coffee_backend.db.session import dispose_db_state, init_db_state
from coffee_backend.services.method_profile_service import seed_method_profiles

configure_logging()
logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    def __init__(self, app: Callable[[Request], Awaitable[Response]]):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        request_id = request.headers.get("x-request-id") or str(uuid4())
        token = request_id_ctx_var.set(request_id)

        async def send_wrapper(message: dict) -> None:
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx_var.reset(token)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info("app.startup", extra={"app_env": resolved_settings.app_env})
        init_db_state(app.state, settings=resolved_settings)
        session_factory = app.state.db_sessionmaker
        with session_factory() as db:
            seed_method_profiles(db)
        try:
            yield
        finally:
            dispose_db_state(app.state)
            logger.info("app.shutdown")

    app = FastAPI(
        title="Coffee Optimiser Backend",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    if resolved_settings.enable_request_id_middleware:
        app.add_middleware(RequestIDMiddleware)

    cors_allowed_origins = resolved_settings.cors_allowed_origins
    cors_origin_regex = None
    if not cors_allowed_origins and resolved_settings.app_env.lower() in {"local", "dev", "development"}:
        cors_allowed_origins = [
            "http://localhost",
            "http://127.0.0.1",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        cors_origin_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^null$"

    if cors_allowed_origins or cors_origin_regex:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_allowed_origins,
            allow_origin_regex=cors_origin_regex,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(APIError)
    async def handle_api_error(_: Request, exc: APIError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code, "fields": exc.fields},
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_: Request, __: IntegrityError) -> ORJSONResponse:
        exc = ConflictError("Resource conflict")
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code, "fields": exc.fields},
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
    app.include_router(methods.router, prefix="/api/v1")
    return app


app = create_app()
