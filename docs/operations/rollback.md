# Rollback (Release 0)

**Document ID:** OPS-002  
**Status:** Active for R0

## Application

1. Stop the app process
2. `git checkout <previous-tag>` (e.g. `v0.1.0` or prior `v0.2.0` candidate)
3. Reinstall lockfile: `pip install -r requirements/dev.txt`
4. Restore DB dump if schema incompatible
5. Restore `media/` if needed
6. Start app; verify `GET /api/v1/health/`
7. Smoke: login → list organizations

## Migrations

Prefer reversible migrations. If a forward migration cannot be reversed safely, restore the pre-migration database snapshot instead of `migrate <app> <older>`.

## Release 0 tags

| Tag | Content |
|-----|---------|
| `v0.1.0` | Skeleton |
| `v0.2.0` | Full R0 foundation (auth → reporting) |
