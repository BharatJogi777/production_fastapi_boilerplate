# Architecture and engineering conventions

## Architecture layers

- `api/`: HTTP transport, routing, middleware and dependency composition.
- `modules/<feature>/`: feature-first vertical slices (routes, controller, schemas, service, repository, models).
- `core/`: settings, security primitives, logging and application lifecycle.
- `common/`: cross-cutting exceptions and stable application contracts.
- `shared/`: reusable application-level schemas, pagination, envelopes and serializers.
- `utils/`: pure generic helpers with no application side effects.
- `infrastructure/`: technical adapters for databases, cache, messaging and HTTP transport.
- `clients/`: typed provider-specific outbound adapters.
- `migrations/`: versioned schema changes; never run migrations in web worker startup.

## Dependency direction

HTTP adapters call application services. Services own business policy and transaction boundaries. Repositories own persistence queries and never commit. Infrastructure implements technical integrations. Shared/core/infrastructure must not import business feature modules. Provider-specific DTOs remain inside the provider client.

Use interfaces/Protocols only at actual substitution or testing boundaries. Avoid generic repository frameworks, service locators, speculative event buses and empty abstraction folders.

## Service boundary

Each microservice owns its database, schema, migrations, API contract, deployment and release lifecycle. Do not share ORM models or repositories between independently deployed services. Communicate through versioned APIs or asynchronous messages. Use the outbox/inbox pattern when reliable database-to-message publication is required.

## Database and transactions

Use one request-scoped AsyncSession. Repository methods may add/flush/query but must not commit. Application services commit or roll back the unit of work. Keep transactions short and never make network calls while holding a DB transaction. Use Alembic as schema source of truth. SQLite is for fast tests only; PostgreSQL integration tests are required before release.

## Reliability

1. Configure explicit outbound timeouts and bounded connection pools.
2. Retry only idempotent operations; never blindly retry payment/email writes.
3. Use idempotency keys for externally retried writes.
4. Bound concurrency and pool sizes against downstream capacity.
5. Never log credentials, tokens, passwords or sensitive payloads.
6. Validate and propagate request IDs.
7. Keep liveness dependency-independent; readiness checks mandatory dependencies.
8. Run migrations as a release job, not in each web worker.
9. Add rate limiting, circuit breakers, metrics and tracing according to the service's deployment and threat model.

See [service template guide](service-template.md), [production readiness](production-readiness.md) and [testing strategy](testing.md).
