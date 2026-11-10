from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api import router
from app.core import get_settings, configure_logging, RequestContextMiddleware, SecurityHeadersMiddleware
from app.db import engine

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("application_starting", environment=settings.app_env)
    yield
    await engine.dispose()
    logger.info("application_stopped")

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug, docs_url="/docs" if settings.app_env != "production" else None, redoc_url="/redoc" if settings.app_env != "production" else None, openapi_url="/openapi.json" if settings.app_env != "production" else None, lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type", "X-Request-ID"])
    app.include_router(router, prefix=settings.api_v1_prefix)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("request_validation_failed", path=request.url.path)
        return JSONResponse(status_code=422, content={"detail": "Request validation failed", "errors": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return app

app = create_app()
