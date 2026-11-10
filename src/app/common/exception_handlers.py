import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.common.exceptions import ApplicationError

logger = structlog.get_logger()
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.info("application_error", path=request.url.path, status_code=exc.status_code)
        return JSONResponse(status_code=exc.status_code, content={"detail":exc.message})
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("request_validation_failed", path=request.url.path)
        return JSONResponse(status_code=422,
            content={"detail":"Request validation failed","errors":exc.errors()})
    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path)
        return JSONResponse(status_code=500, content={"detail":"Internal server error"})
