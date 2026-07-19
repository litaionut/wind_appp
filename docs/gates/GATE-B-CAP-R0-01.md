# Gate B Report — CAP-R0-01 Application Skeleton

**Report ID:** GATE-B-2026-07-19-001  
**Presenter:** Architect Agent / Coordinator Agent  
**Date:** 2026-07-19  
**Status:** Approved by human product owner (2026-07-19) — AD-002  

---

## Capability

**CAP-R0-01** — Application skeleton, development environment, health-check endpoint, automated test pipeline, initial repo docs.

## Objective

Create a runnable, tested Django baseline so later R0 capabilities have a safe integration point.

## Current status

**Architecture proposal — waiting for approval (Gate B).**  
Gate A approved (UD-001, AD-001, UD-004, UD-005). No production code yet.

## Confirmed decisions

| ID | Statement |
|----|-----------|
| UD-001 | Vision + operating model adopted |
| AD-001 | Django modular monolith + DRF + PostgreSQL |
| UD-004 | CAP-R0-01 is first implementation after Gate B |
| UD-005 | Application language is English |
| UD-002 / UD-003 | Deferred (frontend / auth details) |

## Assumptions

| ID | Assumption |
|----|------------|
| A-CAP-01 | Docker Desktop (or equivalent) available for local Postgres |
| A-CAP-02 | Repository will use GitHub Actions (repo on GitHub) |
| A-CAP-03 | Python 3.12 is acceptable baseline |

## Proposed implementation

Minimal backend that:

1. Boots locally with Docker Compose (Postgres) + Django runserver/uvicorn-equivalent (Django `runserver` for R0.1)
2. Exposes `GET /api/v1/health/` returning English JSON
3. Has pytest coverage for the health endpoint
4. Has CI that runs ruff + pytest
5. Documents setup/rollback in README + release notes draft for `v0.1.0`

### Health response (proposed contract)

```json
{
  "status": "ok",
  "service": "wind-platform-api",
  "api_version": "v1"
}
```

HTTP **200** when the process handles the request.  
No DB check in this increment (see non-scope).

## Engineering methodology

N/A — no engineering calculations. Stack per AD-001.

## Architecture impact

### Repository layout (to create at Gate C)

```text
Wind_app/
  README.md
  .gitignore
  .github/workflows/ci.yml
  docker-compose.yml
  requirements/
    base.in
    base.txt
    dev.in
    dev.txt
  backend/
    manage.py
    config/
      __init__.py
      settings/
        base.py
        local.py
        test.py
      urls.py
      wsgi.py
      asgi.py
    apps/
      core/
        apps.py
        api/
          views.py      # health
          urls.py
        tests/
          test_health.py
  docs/                 # already exists
```

### Domain entities

None (no migrations beyond Django built-ins if any; preferably zero custom models).

### API

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/api/v1/health/` | None | 200 + JSON (English keys/values) |

### Background jobs / files / integrations

None.

### Calculation design

None.

## Security impact

| Topic | Impact |
|-------|--------|
| Auth | None yet (intentional) |
| Org isolation | N/A — no tenant data |
| Health endpoint | Public; must not expose secrets, versions of dependencies, or env details |
| Secrets | `SECRET_KEY` and DB credentials via env / `.env` (gitignored) |
| DEBUG | `True` only in local settings |

## Increment plan (Gate C steps — after approval)

1. Init gitignore, Compose, requirements lock  
2. Create Django project + `apps.core`  
3. Implement health view + URL routing  
4. Add pytest + health test  
5. Add GitHub Actions CI  
6. Update README (English), changelog, rollback notes  
7. Submit for Gate D  

**Single PR / single capability.**

## Tests and validation

| Test | Expected |
|------|----------|
| `test_health_returns_200` | Status 200 |
| `test_health_body_status_ok` | `status == "ok"` |
| CI on PR | ruff + pytest green |

No numerical validation.

## Risks and limitations

| Item | Notes |
|------|-------|
| No readiness/DB probe | Deferred to backlog |
| No frontend | UD-002 deferred |
| No auth | UD-003 deferred |
| Windows + Docker | Documented; product owner on Windows |

### Explicit non-scope

Auth, orgs, projects, PostGIS, Celery, frontend, domain models, i18n (English-only per UD-005).

## Acceptance criteria

- [ ] Local start documented and works with Compose + Django  
- [ ] `GET /api/v1/health/` → 200 + agreed JSON  
- [ ] All API strings English  
- [ ] Pytest covers health  
- [ ] CI runs on PR  
- [ ] No custom domain models  
- [ ] Secrets not committed  
- [ ] Gate D clean of blocker/major  
- [ ] Gate E approval before merge to protected main / tag `v0.1.0`

## Decision required

| ID | Decision | Options | Recommendation |
|----|----------|---------|----------------|
| **AD-002** | Approve CAP-R0-01 technical design in this report (layout, health contract, liveness-only, pip-tools, GitHub Actions, Python 3.12, `apps.core`) | Approve / Amend / Reject | **Approve** |

Optional amendments you may request now (not separate IDs unless you choose them):

- Use Poetry instead of pip-tools  
- Add DB check to health immediately  
- Use `/health` without `/api/v1` prefix  

---

**Coordinator recommendation:** Approve **AD-002**. After approval, Coordinator assigns Developer Agent for Gate C only within this scope. No other capabilities in the same PR.
