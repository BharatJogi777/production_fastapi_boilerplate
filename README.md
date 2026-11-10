# Production FastAPI Boilerplate

Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2 async, PostgreSQL, Alembic, JWT, Argon2, Docker and pytest.

## Start
1. cp .env.example .env; generate SECRET_KEY with openssl rand -hex 32.
2. docker compose up -d db
3. uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"
4. alembic upgrade head
5. uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000

Docs: /docs in non-production. Endpoints: GET /api/v1/health/live, GET /api/v1/health/ready, POST /api/v1/auth/register, POST /api/v1/auth/login, GET /api/v1/users/me.

## Design
Router -> Service -> Repository -> SQLAlchemy. Routers own HTTP, services own use cases, repositories own persistence. Keep abstractions purposeful; don't add interfaces without a real substitution boundary.

## Quality
pytest; ruff check .; ruff format --check .; mypy src.

## Before public deployment
Use a secret manager and rotate keys; explicit CORS/host allow-lists; TLS at trusted ingress; distributed rate limiting at gateway/Redis; email verification, password reset, refresh-token rotation, lockout and audit events; migrations as a release job; DB backups/PITR and pool sizing; metrics/traces; non-root containers and dependency scanning; graceful draining and readiness probes. This is a baseline, not a compliance certification. Threat-model and review before production use.
