# Research Brief — CAP-R0-01 Application Skeleton

**Document ID:** RES-R0-01  
**Status:** Complete for Gate A (non-calculation capability)  
**Date:** 2026-07-19

---

## Research question

What is a minimal, industry-standard foundation for a multi-tenant engineering web platform that will later host geospatial and numerical workloads?

## Applicable standards

| Topic | Reference | Access |
|-------|-----------|--------|
| HTTP API health | Common practice (Kubernetes liveness/readiness concepts) | Public |
| Security baseline | OWASP ASVS (high-level awareness for later caps) | Public summaries |
| Geospatial (later) | OGC, EPSG registry | R1 research |
| Wind engineering | IEC 61400 series etc. | **Not required for CAP-R0-01** |

## Methodology options (stack)

| Option | Pros | Cons |
|--------|------|------|
| Django + DRF + PostgreSQL | Auth/admin/ORM maturity; fits modular monolith | Heavier than micro-frameworks |
| FastAPI + SQLAlchemy + PostgreSQL | Fast async; explicit | More DIY for admin/auth patterns |
| .NET / Java | Enterprise ecosystems | Team/tooling mismatch unless chosen explicitly |

## Recommended methodology

Django modular monolith + DRF + PostgreSQL (AD-001), health endpoint, pytest, GitHub Actions (or equivalent CI).

## Equations / units

None.

## Assumptions

- Team accepts Python backend
- Docker available for local Postgres

## Limitations

- No claim of production hardening in CAP-R0-01
- Health endpoint design (liveness vs readiness) deferred to Gate B

## Validation examples

- `GET /health` → 200  
- CI runs test suite on sample PR  

## References

- Django documentation (djangoproject.com) — framework of record for implementation  
- Django REST Framework documentation  
- PostgreSQL documentation  
- OWASP ASVS (for later security capabilities)

## Unresolved engineering decisions

- Exact CI provider path (GitHub Actions assumed if repo on GitHub)
- Health payload schema

## Recommendation

Proceed to Gate B for CAP-R0-01 after UD-001/AD-001/UD-004 approval. No calculation research required for this increment.
