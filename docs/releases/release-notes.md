# Release Notes

## 0.2.0 — Release 0 foundation complete — 2026-07-19

Secure multi-tenant foundation: authentication, organizations/projects with RBAC-ish roles, audit trail, project files, versioned calculation runs (stub method), and basic report artifacts. English UI/API strings. Automated E2E foundation test included.

### Upgrade

1. `pip install -r requirements/dev.txt`
2. `docker compose up -d db`
3. `python backend/manage.py migrate`
4. Restart app

### Rollback

See `docs/operations/rollback.md`. Tag `v0.1.0` is the previous skeleton-only release.

---

## 0.1.0 — Application skeleton — 2026-07-19

Django health endpoint, Compose Postgres, CI, governance docs.
