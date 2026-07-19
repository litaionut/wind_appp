# Rollback Procedures

**Document ID:** OPS-002  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Pre-implementation note

Concrete commands will be filled when CAP-R0-01 defines the runtime (Docker Compose, etc.).

## Template for each release

```text
Release: vX.Y.Z
Previous: vX.Y.Z-1
Migrations: <forward> / <backward>
DB snapshot: <location/policy>
App rollback: checkout tag + redeploy
Verification: GET /health → 200; smoke tests; permission check
Owner: <role>
```

## Current state

No production release exists. Rollback for documentation-only package: revert Git commit(s) that added `/docs`.
