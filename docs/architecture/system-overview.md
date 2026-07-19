# System Overview

**Document ID:** ARCH-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Architectural style

**Modular monolith** (default through at least Release 3).

Rationale:

- Clear domain modules with enforced boundaries
- Single deployable unit for early operational simplicity
- Shared PostgreSQL transaction boundaries for audit + domain consistency
- Distributed services only via approved ADR with documented reason

## Default technology direction

| Layer | Proposed choice | Notes |
|-------|-----------------|-------|
| Backend | Django | Domain modules as Django apps |
| API | Django REST Framework | Versioned HTTP API (`/api/v1/`) |
| Database | PostgreSQL | Primary system of record |
| Geospatial | PostGIS | Required from R1; optional prep in R0 |
| Async jobs | Celery + Redis (or approved equivalent) | Long-running calculations |
| File storage | S3-compatible object storage | Local filesystem adapter for dev |
| Frontend | Separate SPA (framework TBD — see UD-002) | Not embedded Django templates for product UI |
| Auth | Session/JWT strategy TBD — see UD-003 | Must support org-scoped authorization |

Any deviation requires an Architecture Decision Record in `docs/architecture/decisions/`.

## Logical modules (domains)

```text
platform/
  identity/          # users, auth
  organizations/     # orgs, membership
  projects/          # projects, project membership
  permissions/       # RBAC
  audit/             # audit events
  files/             # file metadata + storage adapters
  calculations/      # calculation runs, method registry, logs
  reporting/         # artifacts, basic generation
  gis/               # R1+
  meteo/             # R2+
  energy/            # R3+
  environment/       # R5+
  site_suitability/  # R6+
  operations/        # R7+
  electrical/        # R8+
  financial/         # R8+
  hybrid/            # R9+
```

## Cross-cutting concerns

- Organization isolation on every data access path
- Explicit units for engineering values
- Calculation-method versioning
- Structured logging and correlation IDs
- Feature flags for experimental methods
- Reversible migrations preferred

## Proposed repository structure

```text
Wind_app/
  README.md
  LICENSE
  .gitignore
  pyproject.toml / requirements/     # exact layout TBD at CAP-R0-01
  docker-compose.yml                 # local Postgres (+ Redis later)
  Makefile or justfile               # developer commands
  .github/workflows/ci.yml           # or approved CI system
  backend/
    manage.py
    config/                          # Django settings, urls, asgi/wsgi
    apps/
      identity/
      organizations/
      projects/
      permissions/
      audit/
      files/
      calculations/
      reporting/
    tests/                           # cross-app integration tests
  frontend/                          # created after UD-002
  docs/                              # system of record (this tree)
  scripts/                           # ops helpers
  benchmarks/                        # validation datasets (later)
```

## Non-goals for architecture (R0)

- Microservices split
- Multi-region active-active
- Custom CFD engine
- Embedding proprietary vendor SDKs without legal review
