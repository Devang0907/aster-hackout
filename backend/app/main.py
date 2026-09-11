from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import admin, factories, health, insights, operational, reporting
from app.core.config import get_settings
from app.core.database import connect_database, disconnect_database
from app.services.errors import ServiceError


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.database_url is None:
        raise RuntimeError("DATABASE_URL must be configured")
    await connect_database()
    try:
        yield
    finally:
        await disconnect_database()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @application.exception_handler(ServiceError)
    async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    application.include_router(health.router)
    application.include_router(admin.router, prefix="/api/v1")
    application.include_router(factories.router, prefix="/api/v1")
    application.include_router(reporting.router, prefix="/api/v1")
    application.include_router(operational.router, prefix="/api/v1")
    application.include_router(insights.router, prefix="/api/v1")
    return application


app = create_app()
