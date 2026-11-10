import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient

from app.common.exception_handlers import register_exception_handlers
from app.common.exceptions import ConflictError
from app.infrastructure.http.exceptions import ExternalServiceError


@pytest.fixture
def error_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/conflict")
    async def conflict() -> None:
        raise ConflictError("Already exists")

    @app.get("/http-error")
    async def http_error() -> None:
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/upstream")
    async def upstream() -> None:
        raise ExternalServiceError("catalog", "connection refused")

    @app.get("/unexpected")
    async def unexpected() -> None:
        raise RuntimeError("sensitive internal detail")

    return app


@pytest.mark.asyncio
async def test_application_error_uses_common_envelope(error_app: FastAPI) -> None:
    async with AsyncClient(transport=ASGITransport(app=error_app), base_url="http://test") as client:
        response = await client.get("/conflict")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICTERROR"
    assert response.json()["error"]["message"] == "Already exists"


@pytest.mark.asyncio
async def test_http_error_uses_common_envelope(error_app: FastAPI) -> None:
    async with AsyncClient(transport=ASGITransport(app=error_app), base_url="http://test") as client:
        response = await client.get("/http-error")
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Not found"


@pytest.mark.asyncio
async def test_upstream_error_does_not_leak_provider_details(error_app: FastAPI) -> None:
    async with AsyncClient(transport=ASGITransport(app=error_app), base_url="http://test") as client:
        response = await client.get("/upstream")
    assert response.status_code == 502
    assert "connection refused" not in response.text


@pytest.mark.asyncio
async def test_unexpected_error_does_not_leak_internal_details(error_app: FastAPI) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=error_app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        response = await client.get("/unexpected")
    assert response.status_code == 500
    assert "sensitive internal detail" not in response.text
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
