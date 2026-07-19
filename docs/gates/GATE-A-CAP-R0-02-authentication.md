# Gate A Report — CAP-R0-02 Authentication Baseline

**Report ID:** GATE-A-2026-07-19-002  
**Presenter:** Coordinator Agent (Product + Research)  
**Date:** 2026-07-19  
**Status:** Approved (2026-07-19) — UD-007, UD-003=A, SD-001=disabled; standing approval UD-008  

---

## Capability

**CAP-R0-02** — Authentication baseline (users, admin session login, API token login, `me` endpoint).

## Objective

Introduce authenticated identity so later organization/project isolation can be built safely.

## Current status

**Waiting for approval (Gate A).** Requirements and research drafted. No auth code written yet.

## Confirmed decisions

| ID | Statement |
|----|-----------|
| UD-001 | Vision + operating model |
| AD-001 / AD-002 | Django + DRF + PostgreSQL skeleton |
| UD-005 | Application language English |
| UD-006 | CAP-R0-01 accepted (`v0.1.0`) |
| UD-002 | Frontend still deferred |

## Assumptions

| ID | Assumption |
|----|------------|
| A-AUTH-01 | Users are created by staff; no public signup marketplace |
| A-AUTH-02 | First API consumers are developers/tools; SPA comes later |
| A-AUTH-03 | Email delivery not available in R0 for reset/verify |

## Proposed implementation

After Gate B:

- Django auth + admin  
- DRF TokenAuthentication  
- `POST /api/v1/auth/login/` → token  
- `POST /api/v1/auth/logout/` → revoke token  
- `GET /api/v1/auth/me/` → current user  
- Health remains public  
- Tests + README (English)

## Engineering methodology

N/A (no wind calculations). Security practice per Django/DRF/OWASP ASVS high-level guidance — see research brief.

## Architecture impact

| Area | Impact |
|------|--------|
| Apps | Likely `apps.identity` (or `apps.core` auth package) — finalized at Gate B |
| DB | `authtoken_token` (+ Django auth tables already present) |
| API | `/api/v1/auth/*` |
| Background jobs | None |
| Orgs/projects | Not in this increment |

## Security impact

| Topic | Impact |
|-------|--------|
| Identity | Real passwords/tokens enter the system |
| Org isolation | Still N/A until CAP-R0-03 |
| Brute force | Login endpoint risk — Gate B should add DRF throttle at minimum |
| Public signup | Proposed **disabled** (SD-001) |
| Health | Stays public; must not leak user data |

## Increment plan

1. Gate A approval (this report)  
2. Gate B technical design (endpoints, custom user yes/no, throttles)  
3. Gate C implement CAP-R0-02 only  
4. Gate D tests/review → Gate E  

Next capabilities after acceptance: CAP-R0-03 Organizations → CAP-R0-04 Membership.

## Tests and validation

- Valid/invalid login  
- `me` auth required  
- Health public  
- Inactive user rejected  
- CI green  

## Risks and limitations

| Risk | Mitigation |
|------|------------|
| Choosing wrong token vs JWT | Prefer Token now; JWT when SPA lands (UD-002) |
| Late custom User model pain | Decide at Gate B before many FKs exist |
| No audit of logins yet | Backlog until audit capability |

## Acceptance criteria (Gate A)

- [ ] Scope of CAP-R0-02 accepted (and non-scope clear)  
- [ ] Auth direction decisions recorded (below)  
- [ ] Authorization to proceed to Gate B only (no coding before Gate B)  

## Decision required

| ID | Decision | Options | Recommendation |
|----|----------|---------|----------------|
| **UD-007** | Approve CAP-R0-02 scope (auth baseline as in this report / CAP doc) and proceed to Gate B | Approve / Amend / Reject | **Approve** |
| **UD-003** | API auth mechanism for R0 | **A)** DRF Token (+ session for admin) / **B)** SimpleJWT / **C)** Other | **A — DRF Token** |
| **SD-001** | Public self-registration in this increment | Disabled / Enabled | **Disabled** |

---

**Coordinator recommendation:** Approve UD-007, UD-003 option A, SD-001 Disabled. Then prepare Gate B (no implementation until Gate B approval).
