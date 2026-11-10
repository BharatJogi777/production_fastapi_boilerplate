import logging
import sys
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Literal

import jwt
import structlog
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pwdlib import PasswordHash
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Production FastAPI Boilerplate"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: SecretStr
    access_token_expire_minutes: int = 15
    database_url: str
    cors_origins: list[str] = []
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    log_level: str = "INFO"

    @field_validator("secret_key")
    @classmethod
    def strong_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")
        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def valid_ttl(cls, value: int) -> int:
        if not 1 <= value <= 60:
            raise ValueError("Access token lifetime must be 1-60 minutes")
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

password_hash = PasswordHash.recommended()
def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {"sub": subject, "iat": now, "exp": now + timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(claims, settings.secret_key.get_secret_value(), algorithm="HS256")

def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=["HS256"], options={"require": ["sub", "iat", "exp"]})

def configure_logging() -> None:
    level = get_settings().log_level.upper()
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level, force=True)
    structlog.configure(processors=[structlog.contextvars.merge_contextvars, structlog.processors.add_log_level, structlog.processors.TimeStamper(fmt="iso", utc=True), structlog.processors.format_exc_info, structlog.processors.JSONRenderer()], wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level, logging.INFO)), logger_factory=structlog.stdlib.LoggerFactory())

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, method=request.method, path=request.url.path)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response
