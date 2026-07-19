# AD-002 — CAP-R0-01 Technical Design

**Status:** Approved  
**Date:** 2026-07-19  
**Approved by:** Human product owner (Gate B)  
**Depends on:** AD-001 (approved), UD-004 (approved), UD-005 (approved)

## Context

Need a concrete, minimal technical design for the first implementation increment.

## Decision

1. Django 5.x project under `backend/` with settings modules: `config.settings.base`, `.local`, `.test`, `.production` (production stub only).
2. DRF installed and wired; first endpoint `GET /api/v1/health/`.
3. Health is **liveness-only** in this increment: HTTP 200 + JSON if the app process responds. No database probe yet (readiness split → backlog).
4. Local Postgres via Docker Compose; tests use PostgreSQL service in CI; local pytest may use Postgres from Compose or CI-equivalent.
5. Dependencies managed with `pip-tools` (`requirements.in` → `requirements.txt`) or Poetry — **default: pip-tools** for simplicity.
6. CI: GitHub Actions — lint (ruff) + pytest on pull_request and push to main.
7. All user-facing API message strings in **English** (UD-005).
8. No domain apps yet beyond a thin `apps.core` (health only).

## Consequences

- Fastest path to a green baseline
- Readiness/DB health deferred (explicit non-scope)
- English locked for API responses from day one
