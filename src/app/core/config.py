from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Production FastAPI Boilerplate"
    service_name: str = "fastapi-service"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: SecretStr
    access_token_expire_minutes: int = 15
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout_seconds: float = 30.0
    database_pool_recycle_seconds: int = 1800
    cors_origins: list[str] = Field(default_factory=list)
    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    http_connect_timeout_seconds: float = 3.0
    http_read_timeout_seconds: float = 10.0
    http_write_timeout_seconds: float = 10.0
    http_pool_timeout_seconds: float = 3.0
    http_max_connections: int = 100
    http_max_keepalive_connections: int = 20

    @field_validator("secret_key")
    @classmethod
    def validate_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")
        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_ttl(cls, value: int) -> int:
        if not 1 <= value <= 60:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 60")
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        if not value.startswith("/") or value.endswith("/"):
            raise ValueError("API_V1_PREFIX must start with '/' and must not end with '/'")
        return value

    @field_validator(
        "http_connect_timeout_seconds",
        "http_read_timeout_seconds",
        "http_write_timeout_seconds",
        "http_pool_timeout_seconds",
        "database_pool_timeout_seconds",
    )
    @classmethod
    def validate_timeout(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Timeout values must be greater than zero")
        return value

    @field_validator("http_max_connections", "database_pool_size")
    @classmethod
    def validate_positive_connections(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Connection pool sizes must be at least 1")
        return value

    @field_validator("database_max_overflow", "database_pool_recycle_seconds")
    @classmethod
    def validate_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Database pool values cannot be negative")
        return value

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env == "production":
            if self.debug:
                raise ValueError("DEBUG must be false in production")
            if not self.allowed_hosts or "*" in self.allowed_hosts:
                raise ValueError("Production ALLOWED_HOSTS must be explicit")
            if "*" in self.cors_origins:
                raise ValueError("Wildcard CORS origins are not allowed in production")
        return self


@lru_cache
def get_settings() -> Settings:
    # BaseSettings resolves required values from environment/.env at runtime.
    return Settings(**{})
