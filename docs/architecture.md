# Architecture and engineering conventions

## Dependency direction
HTTP/API adapters depend on application services. Services own business policy and use repository contracts only where there is a real substitution boundary. Infrastructure implements technical concerns. Feature modules own their business rules. Generic helpers must not import FastAPI, SQLAlchemy or a feature module.

## Layer responsibilities
- `modules/<feature>/routes.py`: HTTP method, path, dependencies, status and response model.
- `controller.py`: maps transport schemas to use cases and maps results back.
- `service.py`: use cases, business invariants and transaction boundary.
- `repository.py`: persistence queries; no HTTP or business policy.
- `schemas.py`: validated input/output contracts. Never return ORM entities directly.
- `models.py`: persistence mappings only.
- `dependencies.py`: feature-specific dependency composition.
- `shared/`: reusable application components (pagination, API base schemas, response envelope).
- `utils/`: generic deterministic helpers without application side effects.
- `common/`: cross-cutting errors/types/constants; not a dumping ground.
- `infrastructure/`: database, cache, messaging and outbound transport implementations.
- `clients/`: typed adapters per external provider, sharing the lifespan-managed HTTPX pool.

## Reliability rules
1. Set connect/read/write/pool timeouts on outbound HTTP clients.
2. Retry only operations proven idempotent; never blindly retry payment or email POST requests.
3. Bound connection pools and size them with worker count and upstream capacity in mind.
4. Never log credentials, authorization headers, tokens, passwords or sensitive payloads.
5. Keep DB transactions short; do not make network calls while holding a DB transaction.
6. Add idempotency keys for externally retried write operations.
7. Use request IDs for log correlation; validate untrusted inbound IDs.
8. Keep liveness independent of dependencies; readiness checks required dependencies.
9. Run migrations as a release step, not in every web worker.
10. Add abstractions only after a real use case or stable contract exists.

## Production rollout checklist
Configure TLS at ingress, secrets manager/key rotation, production CORS/host allowlists, distributed rate limiting, refresh-token rotation/revocation, audit trails, backups/PITR, migration job, metrics/traces/alerting, dependency/image scanning, worker/pool sizing, graceful termination and rollback. These require deployment infrastructure and are not faked by this starter.
