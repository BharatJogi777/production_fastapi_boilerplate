# Production FastAPI Microservice Template

A reusable FastAPI foundation for independently deployable microservices. It provides a modular application structure, async SQLAlchemy/PostgreSQL, Alembic, JWT/Argon2 examples, request correlation, centralized errors, outbound HTTP infrastructure, Docker and tests.

**This is a starter template, not production certification.** Each service must configure its own secrets, data store, deployment, SLOs and operational integrations.

## Architecture

See:
- [Architecture and engineering conventions](docs/architecture.md)
- [Creating a service from this template](docs/service-template.md)
- [Production readiness checklist](docs/production-readiness.md)
- [Testing strategy](docs/testing.md)

```text
src/app/
├── main.py
├── api/                 # router, dependencies, middleware
├── core/                # settings, security, logging, lifecycle
├── common/              # errors and stable cross-cutting contracts
├── shared/              # reusable schemas, pagination, responses
├── utils/               # pure helpers
├── infrastructure/      # database and technical adapters
├── clients/             # provider-specific outbound clients
└── modules/             # feature-first business modules
migrations/              # Alembic migrations
tests/
docs/
```

## Quick start

```bash
cp .env.example .env
# Set a unique secret and database password in .env
openssl rand -hex 32
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

API docs are available at `/docs` outside production. Sample endpoints include `/api/v1/health/live`, `/api/v1/health/ready`, `/api/v1/auth/register`, `/api/v1/auth/login` and `/api/v1/users/me`.

## Quality checks

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

For PostgreSQL-backed validation, run the disposable database integration environment described in [testing.md](docs/testing.md). The default SQLite suite is not a substitute.

## Reuse model

Keep generic infrastructure in the template. Keep payment, order, notification and other business behavior inside the service that owns it. Optional integrations should be added only when a service needs them. See [service-template.md](docs/service-template.md).
