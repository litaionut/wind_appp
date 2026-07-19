# Test Strategy

**Document ID:** QA-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Principles

1. Test Agent designs cases from **approved requirements**, not from implementation anecdotes.
2. “Runs without error” ≠ validated.
3. Numerical tests use documented tolerances.
4. Permission and org-isolation tests are mandatory from the first domain data capability.
5. Migrations are tested forward (and backward when reversible).

## Test layers

| Layer | Purpose | When |
|-------|---------|------|
| Unit | Pure functions, validators, permissions helpers | Every increment |
| API | Contract, authz, validation errors | From first API |
| Integration | DB + services | From first persistence |
| Permission / isolation | Cross-org negative tests | From orgs/projects |
| File import | Parsers, bad files | From files/METEO |
| Migration | Schema upgrade/downgrade | Every migration |
| Numerical | Hand calc / published / benchmark | Every engineering method |
| Regression | Prior validated fixtures | After first validated method |
| E2E | Critical user journeys | Release exits |
| Performance | Hot paths / large TS | When justified |

## Independence

Developers may add tests during Gate C. Gate D requires Test Agent review/expansion for independence and coverage of acceptance criteria.
