# Monitoring (Release 0)

**Document ID:** OPS-004  
**Status:** Active for R0

## Signals

| Signal | How |
|--------|-----|
| Liveness | `GET /api/v1/health/` → 200 |
| CI | GitHub Actions workflow on PR/push |
| App logs | stdout from `runserver` / process manager |
| Audit trail | `AuditEvent` table / org audit API |

## Not yet in R0

- APM (Datadog/Sentry/etc.)
- Metrics dashboards
- DB readiness probe on health endpoint
