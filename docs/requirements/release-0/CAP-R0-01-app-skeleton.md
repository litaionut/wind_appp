# CAP-R0-01 — Application Skeleton & Dev Foundation

**Capability ID:** CAP-R0-01  
**Status:** Accepted (UD-006) — Released candidate `v0.1.0`  
**Class:** Foundation  
**Proposed version tag:** `v0.1.0`  
**Language:** English (UD-005)

---

## 1. Problem statement

The repository has no application runtime, no reproducible development environment, no health signal, and no automated test pipeline. Without this foundation, later modules cannot be developed, tested, or released safely.

## 2. User role / story

As a **platform engineer**, I need a runnable backend skeleton with a health-check and CI so that every subsequent capability can be integrated into a known-good baseline.

## 3. Engineering objective

Establish a minimal, tested Django application that boots locally, exposes a health endpoint, and fails CI on test failure.

## 4. Scope

- Project layout under `backend/`
- Django project + settings split (base / local / test)
- PostgreSQL via Docker Compose for local/dev
- `GET /api/v1/health/` (liveness-only) returning English JSON
- Pytest with health tests
- GitHub Actions CI (ruff + pytest)
- Root README (English) with setup instructions
- Keep `/docs` as system of record
- `.gitignore`, pip-tools lockfiles

## 5. Non-scope

- Authentication, organizations, projects
- Frontend application
- PostGIS, Celery/Redis
- Calculation engines
- Production Kubernetes manifests
- Domain engineering models
- DB readiness probe
- i18n / non-English UI (English only)

## 6. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Developer can start API locally with documented commands |
| FR-02 | Health endpoint returns HTTP 200 when app is up |
| FR-03 | Automated tests cover health endpoint |
| FR-04 | CI runs tests on pull requests |
| FR-05 | Documentation explains setup and rollback of this increment |
| FR-06 | User-facing API messages are in English |

## 7. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Cold start of local stack documented < 15 minutes on a developer machine |
| NFR-02 | No secrets committed |
| NFR-03 | Deterministic dependency resolution via lockfile |
| NFR-04 | Application language English (UD-005) |

## 8. Inputs / outputs

- Inputs: developer machine, Docker, Python 3.12 toolchain
- Outputs: running API, CI green, docs updated

## 9. Edge cases

- DB unavailable: health still returns 200 (liveness-only by design in AD-002)
- CI: Postgres service container for tests

## 10. Dependencies

- UD-001, AD-001, UD-004, UD-005 (approved)
- AD-002 (awaiting Gate B)

## 11. Acceptance criteria

- [ ] `backend/` boots with documented command
- [ ] Health endpoint returns 200 with agreed English JSON
- [ ] Automated test for health passes locally and in CI
- [ ] README + release notes for `v0.1.0` draft exist
- [ ] No domain models beyond health app shell
- [ ] Gate D review: no blocker/major
- [ ] Gate E product-owner approval

## 12. Future extensions (backlog only)

- Readiness vs liveness split (DB probe)
- OpenAPI skeleton
- Pre-commit hooks
- Devcontainer

## Gate references

- Gate A: approved — `docs/gates/GATE-A-M0.0-foundation-package.md`
- Gate B: pending — `docs/gates/GATE-B-CAP-R0-01.md`
