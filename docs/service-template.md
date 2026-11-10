# Creating a microservice from this template

This repository is a reusable service foundation, not a shared runtime that all services must deploy together. Each service owns its code, database, migrations, configuration, deployment and release lifecycle.

## 1. Bootstrap a new service

1. Create a new repository from this template (GitHub's **Use this template** action) or clone and push it to a new repository.
2. Set a unique `APP_NAME` and `SERVICE_NAME`.
3. Generate a new `SECRET_KEY`; never reuse a secret between services or environments.
4. Set a service-specific PostgreSQL database and credentials.
5. Replace sample business modules (`auth`, `users`) if the service does not need them. Keep `health` and generic infrastructure.
6. Add only the infrastructure integrations this service actually uses.
7. Create an Alembic migration for every schema change. Never use `metadata.create_all` in deployed application startup.
8. Update the README with the service purpose, API contract, dependencies, run commands and operational ownership.

## 2. Module convention

A feature module owns its complete vertical slice:

```text
modules/<feature>/
  routes.py          # HTTP paths, status codes, response models
  controller.py      # transport-to-use-case adaptation
  schemas.py         # request and response DTOs
  service.py         # business rules and transaction boundary
  repository.py      # database queries
  models.py          # SQLAlchemy mappings
  dependencies.py    # dependency composition
```

Only create files that have a real responsibility. A tiny feature does not need a controller and a repository merely to satisfy a folder convention. Do not import one microservice's ORM models or repositories into another microservice.

## 3. Dependency direction

```text
routes -> controller -> service -> repository interface
                                      ^
                                      |
                         infrastructure implementation

service -> domain/common contracts
infrastructure -> external systems
```

Business modules may depend on shared contracts. Shared/core/infrastructure must not import business feature modules. Keep provider-specific request/response models inside `clients/<provider>`.

## 4. Database and transactions

- One database per service boundary; do not share tables across microservices.
- Use request-scoped `AsyncSession`; repositories flush, services commit/rollback.
- Do not perform outbound network calls while a database transaction is open.
- Use Alembic migrations as the schema source of truth.
- Run migrations once as a release/deployment job, not in every Uvicorn worker.
- Size pool limits against total replicas × workers × pool size and the database connection budget.
- Add PostgreSQL integration tests; SQLite tests are fast feedback only.

## 5. Operational requirements

Before production: configure TLS at ingress, secret management/rotation, restrictive CORS and host allowlists, distributed rate limiting where needed, metrics/traces/alerts, backups/PITR, migration rollback strategy, dependency/image scanning, resource limits, graceful shutdown, and load tests.

## 6. Service ownership

Every service must document its owner, on-call route, data classification, SLOs, dependencies, retry/idempotency behavior, dashboard, alert policy, backup/restore procedure and deployment rollback procedure.
