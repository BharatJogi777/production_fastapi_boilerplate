from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.router import api_router
from app.common.exception_handlers import register_exception_handlers
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.database.session import engine

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
    app = FastAPI(title=settings.app_name, debug=settings.debug,
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.app_env != "production" else None,
        openapi_url="/openapi.json" if settings.app_env != "production" else None,
        lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
        allow_credentials=True, allow_methods=["GET","POST","PUT","PATCH","DELETE"],
        allow_headers=["Authorization","Content-Type","X-Request-ID"])
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app

app = create_app()
