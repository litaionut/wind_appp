# AD-001 — Modular Django Monolith

**Status:** Approved  
**Date:** 2026-07-19  
**Approved by:** Human product owner (Gate A)  
**Deciders:** Architect Agent → human product owner  

## Context

Need a maintainable backend for a multi-tenant engineering platform with strong consistency for audit and permissions, without early microservices complexity.

## Decision

Use a **modular Django monolith** with Django REST Framework, PostgreSQL, and domain modules as Django apps. Introduce PostGIS at R1. Introduce background workers when first long-running job appears.

## Consequences

- Faster R0 delivery and simpler transactions
- Module boundaries must be disciplined (no cross-app spaghetti)
- Extraction to services later possible but not free

## Alternatives considered

- Separate microservices per domain — rejected for R0 (ops cost)
- FastAPI modular monolith — viable alternative; Django preferred for admin, auth, ORM maturity unless UD overrides
