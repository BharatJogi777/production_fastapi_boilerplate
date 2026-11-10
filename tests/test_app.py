import os

# Provide isolated defaults before importing modules that construct Settings/engines.
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-that-is-long-enough-123456")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test-bootstrap.db")
os.environ.setdefault("ALLOWED_HOSTS", '["testserver","localhost"]')
os.environ.setdefault("CORS_ORIGINS", "[]")
os.environ.setdefault("APP_ENV", "test")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db_session
from app.main import create_app
from app.domain import User  # noqa: F401

@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async def override_session():
        async with sessions() as session:
            yield session
    app = create_app()
    app.dependency_overrides[get_db_session] = override_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    await engine.dispose()

@pytest.mark.asyncio
async def test_health_and_auth_flow(client):
    assert (await client.get("/api/v1/health/live")).status_code == 200
    payload = {"email": "dev@example.com", "password": "long-test-password-123"}
    created = await client.post("/api/v1/auth/register", json=payload)
    assert created.status_code == 201
    assert "hashed_password" not in created.json()
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 409
    login = await client.post("/api/v1/auth/login", data={"username": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]

@pytest.mark.asyncio
async def test_auth_and_validation_failures(client):
    assert (await client.get("/api/v1/users/me")).status_code == 401
    invalid = await client.post("/api/v1/auth/register", json={"email": "nope", "password": "tiny"})
    assert invalid.status_code == 422
