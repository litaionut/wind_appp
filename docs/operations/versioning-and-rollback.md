# Versioning and Rollback Strategy

**Document ID:** OPS-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Source-code versioning

- Git with protected `main`
- Short-lived feature branches: `feature/CAP-R0-01-app-skeleton`
- Pull requests required
- Automated tests required before merge
- Reviewer approval required
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`)
- Tag every approved release: `vMAJOR.MINOR.PATCH`
- Semantic versioning as in `release-plan.md`

## Feature / calculation versioning

- Method IDs + versions in registry
- Runs store method version, app version, input version, config, user, timestamp, results, warnings, logs
- Equation/default changes → new method version
- Historical runs remain reproducible

## Database safety

- Prefer reversible migrations
- Test forward and backward migrations in CI when feasible
- No destructive production migrations without backup
- Staged migrations for major schema changes
- Document data transformations

## Feature flags

- Incomplete/experimental features behind flags
- Experimental calculation methods never default without approval

## Release recovery package

Each release includes:

1. Source tag  
2. Migration version  
3. Dependency lockfile  
4. Deployment configuration  
5. Release notes  
6. Rollback procedure  
7. Compatibility notes  

## Rollback procedure (generic)

1. Announce maintenance window if needed  
2. Restore previous application artifact/tag  
3. Run documented backward migrations **or** restore DB snapshot if migration not reversible  
4. Verify health-check and smoke tests  
5. Verify critical permission isolation smoke test  
6. Record incident / rollback in `docs/releases/`  

Detailed per-release steps live in `docs/operations/rollback.md` and release notes.
