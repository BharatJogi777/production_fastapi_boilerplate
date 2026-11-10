# Production FastAPI Boilerplate

A modular, production-oriented FastAPI starter with explicit feature modules, reusable shared components, infrastructure adapters, outbound API clients, PostgreSQL/SQLAlchemy async persistence, Alembic, JWT/Argon2, Docker and pytest.

## Architecture
See [architecture and engineering conventions](docs/architecture.md) and [testing strategy](docs/testing.md).

```text
src/app/
├── main.py
├── api/                 # router, dependencies, middleware, exception handlers
├── core/                # settings, security, logging, application lifecycle
├── common/              # cross-cutting exceptions and definitions
├── utils/               # pure generic helpers (datetime, strings, identifiers)
├── shared/              # reusable application components (pagination, schemas, envelopes)
├── infrastructure/      # database, HTTP transport, cache/messaging extension points
├── clients/             # typed external provider clients (payment, notification)
└── modules/             # feature-first modules: auth, users, health, ...
migrations/
tests/
docs/
```

## Layer boundaries
Routes handle HTTP wiring; controllers adapt transport to use cases; services own business rules and transactions; repositories own persistence; schemas define API contracts; models map database records; dependencies compose components. Shared contains reusable application behavior, utils contains stateless framework-independent helpers, infrastructure owns technical integrations, and clients contain provider-specific adapters.

Avoid premature abstractions and empty folders. Keep business rules in their feature: payment fee calculation belongs in payments, not utils.

## Run locally
```bash
cp .env.example .env
# Generate a local secret: openssl rand -hex 32; put it in SECRET_KEY
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

API docs are available at `/docs` outside production. Endpoints: `/api/v1/health/live`, `/api/v1/health/ready`, `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/users/me`.

## Quality commands
```bash
ruff check .
ruff format --check .
mypy src
pytest
```

## Before public deployment
This is a baseline, not production certification. Configure TLS/ingress, managed secrets and key rotation, production CORS/host allowlists, distributed rate limiting, refresh-token rotation/revocation, email verification/password reset, login abuse controls, audit events, PostgreSQL backups/PITR, release migration jobs, metrics/tracing/alerting, dependency and image scanning, worker/connection-pool sizing, graceful termination and rollback. See the architecture guide for the reasoning.
