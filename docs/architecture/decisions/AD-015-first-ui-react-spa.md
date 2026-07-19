# AD-015 — First UI slice (React SPA)

**Status:** Approved  
**Date:** 2026-07-19  
**Depends on:** UD-002, UD-003, UD-010

## Decision

1. SPA under `frontend/` with **React + Vite + TypeScript**.
2. First vertical slice: **login → organizations/projects → project AEP**.
3. Auth remains **DRF Token** stored in `localStorage`; Vite proxies `/api` → Django `:8000`.
4. `django-cors-headers` enabled for direct browser access to API origins in local settings.
5. Interactive map (CAP-R1-03) remains deferred.

## Consequences

- Product can be demoed without Postman.
- Power curves / turbines still created via API/admin until later UI forms.
