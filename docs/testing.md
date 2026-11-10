# Testing strategy

- Unit: pure utilities, validators and service rules using fakes where useful.
- API integration: request/response contracts, auth, authorization, validation and error mapping.
- Database integration: repositories and migrations against disposable PostgreSQL.
- Contract: outbound provider clients with HTTPX MockTransport and provider sandbox tests.
- Failure: DB unavailable, upstream timeout/5xx, malformed provider payload and expired/invalid token.
- Concurrency: unique constraints, idempotency and race conditions.
- Load: representative read/write mix; measure p95/p99, pool saturation and worker concurrency.

The default suite uses SQLite for fast API feedback. SQLite is not a substitute for PostgreSQL behavior.

## PostgreSQL smoke/integration run

Start the local database and set the same URL used by the app:

```bash
docker compose up -d db
export DATABASE_URL='postgresql+asyncpg://app:change-this-local-password@localhost:5432/app'
alembic upgrade head
pytest
```

Use a disposable database for integration tests. Never point tests at production or a shared developer database. Add dedicated test fixtures that create/drop an isolated schema or database before expanding destructive integration coverage.

## Release gate

Run formatting, lint, type checking, all unit/API tests, PostgreSQL migration upgrade tests, integration tests and a representative load/failure test before releasing a service.
