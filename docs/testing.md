# Testing strategy

- Unit: pure utilities, validators and service business rules with repository fakes.
- Integration: repositories and migrations against disposable PostgreSQL.
- API: request/response contracts, auth, permissions, validation and error mapping.
- Contract: outbound provider clients with HTTPX MockTransport and provider sandbox tests.
- Failure: DB unavailable, upstream timeout/5xx, malformed provider payload, expired/invalid token.
- Load: representative read/write mix; measure p95/p99, pool saturation and worker concurrency.

The default test suite uses SQLite for fast API feedback. SQLite is not a substitute for PostgreSQL integration tests; run those against disposable PostgreSQL before release.
