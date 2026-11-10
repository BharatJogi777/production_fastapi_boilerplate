import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.exceptions import ApplicationError
from app.infrastructure.http.exceptions import ExternalServiceError

logger = structlog.get_logger()


def _request_id(request: Request) -> str | None:
    value = getattr(request.state, "request_id", None)
    return str(value) if value else None


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, object]] | None = None,
) -> JSONResponse:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error["details"] = details
    payload: dict[str, object] = {"error": error}
    request_id = _request_id(request)
    if request_id:
        payload["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.info("application_error", path=request.url.path, status_code=exc.status_code)
        return _error_response(
            request,
            status_code=exc.status_code,
            code=exc.__class__.__name__.upper(),
            message=exc.message,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Never echo submitted values: validation input may contain passwords or tokens.
        details = [
            {
                "location": ".".join(str(part) for part in item.get("loc", ())),
                "message": str(item.get("msg", "Invalid value")),
                "type": str(item.get("type", "value_error")),
            }
            for item in exc.errors()
        ]
        logger.warning("request_validation_failed", path=request.url.path)
        return _error_response(
            request,
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "HTTP request failed"
        return _error_response(
            request,
            status_code=exc.status_code,
            code="HTTP_ERROR",
            message=message,
        )

    @app.exception_handler(ExternalServiceError)
    async def external_service_error(
        request: Request, exc: ExternalServiceError
    ) -> JSONResponse:
        logger.warning("external_service_error", service=exc.service, status_code=exc.status_code)
        return _error_response(
            request,
            status_code=502,
            code="UPSTREAM_SERVICE_ERROR",
            message="A dependent service is temporarily unavailable",
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("database_integrity_error", path=request.url.path)
        return _error_response(
            request,
            status_code=409,
            code="DATA_CONFLICT",
            message="The request conflicts with existing data",
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("database_error", path=request.url.path)
        return _error_response(
            request,
            status_code=500,
            code="DATABASE_ERROR",
            message="A database operation failed",
        )

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path)
        return _error_response(
            request,
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
        )
