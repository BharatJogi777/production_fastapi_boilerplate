# Production readiness checklist

This checklist is deliberately explicit: a starter repository cannot certify the infrastructure in which it is deployed.

## Application
- [ ] Production settings reject debug mode, wildcard hosts and wildcard CORS.
- [ ] API schemas are explicit; ORM objects are never serialized directly.
- [ ] All exceptions use the common error envelope and never expose secrets, SQL or provider payloads.
- [ ] Request IDs are returned and included in structured logs.
- [ ] Liveness is dependency-independent; readiness checks required dependencies.
- [ ] Authentication, authorization and abuse controls match the service threat model.

## Data
- [ ] PostgreSQL migrations are reviewed and tested in both upgrade and rollback scenarios.
- [ ] Migration runs as a one-off release job before new application replicas receive traffic.
- [ ] Transactions are short; services own commit/rollback; repositories do not commit.
- [ ] Pool capacity is calculated across all replicas and workers.
- [ ] Backups, point-in-time recovery and restore drills are verified.

## Integrations
- [ ] Connect/read/write/pool timeouts are set.
- [ ] Retries are bounded and only applied to idempotent operations.
- [ ] Writes use idempotency keys where callers may retry.
- [ ] Circuit breaking and bulkheads are added for critical failure-prone dependencies.
- [ ] No outbound network calls occur inside an open database transaction.

## Operations and security
- [ ] TLS, ingress, secret manager and key rotation are configured.
- [ ] Metrics, distributed traces, dashboards and actionable alerts are configured.
- [ ] Rate limiting is distributed when multiple replicas serve the same identity/IP quota.
- [ ] Container runs as non-root with least privilege and pinned/scanned dependencies and images.
- [ ] CPU/memory limits, worker count, graceful termination and rollback are tested.
- [ ] SLOs, ownership, on-call and incident runbooks exist.
- [ ] Load and failure-injection tests cover expected peak traffic.

## Validation boundary
The repository's default tests use SQLite for fast feedback. Run the PostgreSQL integration suite against a disposable PostgreSQL instance before release. Production security controls such as ingress TLS, managed secrets, distributed rate limiting, metrics backends and alerting are environment-level integrations and must be configured by each service team.
