# Release Notes

## 0.1.0 — Application skeleton (accepted) — 2026-07-19

### Summary

First runnable platform baseline: Django API with health-check, local Postgres, automated tests, and CI. No domain engineering features yet. Application language: English.

### Upgrade

1. Install Python 3.12 and Docker.
2. `pip install -r requirements/dev.txt`
3. `copy .env.example .env`
4. `docker compose up -d db`
5. `python backend/manage.py migrate`
6. `python backend/manage.py runserver`

### Rollback

See README “Rollback (CAP-R0-01)” or `docs/operations/rollback.md`.

### Compatibility

- Pre-1.0 foundation (`0.x`)
- No public API compatibility guarantees beyond `/api/v1/health/`

---

## 0.0.0 — Documentation foundation (2026-07-19)

Created the product vision, roadmap, architecture concepts, agent workflow, approval gates, and Release 0 plan. No application runtime.
