# Release Plan

**Document ID:** RP-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Versioning policy (product releases)

| Phase | Version pattern | Meaning |
|-------|-----------------|---------|
| Platform foundation | `0.x.y` | Pre-1.0; R0 and early hardening |
| First stable engineering platform | `1.0.0` | R0 accepted + first engineering module ready for controlled use (decision: with R1 or after R0-only — see UD-001) |
| Breaking API or calculation behaviour | major bump | Historical runs remain readable; new method versions for calc changes |
| Backward-compatible features | minor | |
| Fixes | patch | |

## Near-term release cadence

| Tag (proposed) | Milestone | Contents |
|----------------|-----------|----------|
| `v0.1.0` | M0.1 | Skeleton, health, CI, docs |
| `v0.2.0` | Auth + orgs | After CAP-R0-02/03 |
| `v0.3.0` | Projects + permissions + audit | |
| `v0.4.0` | Files + calculation runs + registry | |
| `v0.5.0` | Reporting + ops + R0 E2E | Candidate R0 exit → Gate E |

Exact tags assigned at Gate E of each increment.

## Release checklist (every tagged release)

- [ ] Source tag
- [ ] Migration version recorded
- [ ] Dependency lockfile committed
- [ ] Deployment configuration documented
- [ ] Release notes updated
- [ ] Rollback procedure updated
- [ ] Compatibility notes recorded
- [ ] CI green
- [ ] Product-owner approval recorded

## Current release status

| Item | Value |
|------|-------|
| Current version | `0.2.0` (Release 0 complete) |
| Active release train | Release 1 (GIS/layout) — high-level until Gate A |
| Blocked on | Product owner start of R1 / CAP-R1-01 |
