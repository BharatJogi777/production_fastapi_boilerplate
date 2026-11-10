# Production FastAPI Boilerplate

Modular FastAPI starter: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy async, PostgreSQL, Alembic, JWT, Argon2, Docker Compose and pytest.

## Structure
```
src/app/
├── main.py
├── api/{router.py,dependencies/authentication.py}
├── core/{config.py,security.py,logging.py}
├── common/{exceptions.py,exception_handlers.py}
├── infrastructure/database/{base.py,session.py}
└── modules/
    ├── auth/{routes.py,controller.py,service.py,schemas.py}
    ├── users/{routes.py,controller.py,service.py,repository.py,models.py,schemas.py}
    └── health/routes.py
migrations/  tests/
```

Request flow: **Router → Controller → Service → Repository → Database**. Routers own HTTP concerns; controllers adapt HTTP to use cases; services own business rules and transaction boundaries; repositories own SQL/persistence; schemas define API contracts; ORM models stay internal. Avoid abstractions without a real substitution boundary.

## Run
```bash
cp .env.example .env
# Set SECRET_KEY to output of: openssl rand -hex 32
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```
Docs: http://localhost:8000/docs (disabled in production).
Endpoints: GET /api/v1/health/live, GET /api/v1/health/ready, POST /api/v1/auth/register, POST /api/v1/auth/login, GET /api/v1/users/me.

## Quality
```bash
ruff check . && ruff format --check . && mypy src && pytest
```

This is a production-oriented baseline, not a certification. Before public deployment add/threat-model distributed rate limiting, refresh-token rotation/revocation, email verification/password reset, login abuse controls, audit events, managed secrets/key rotation, TLS, production CORS/host allow-lists, backups/PITR, release migration jobs, metrics/tracing, dependency/image scanning, graceful shutdown and deployment-specific pool sizing.
