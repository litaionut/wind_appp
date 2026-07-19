# Agent Collaboration Workflow

**Document ID:** AG-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Roles

| Agent | Responsibility |
|-------|----------------|
| **Coordinator** | Roadmap, backlog, gates, conflict resolution, human briefings; does **not** implement unless explicitly assigned a specialist role |
| **Product** | Requirements, scope control, acceptance criteria |
| **Research** | Standards, methods, equations, references, validation examples |
| **Architect** | Domain model, APIs, ADRs, security impact, increments |
| **Developer** | Implements only approved scope; migrations; implementation notes |
| **Test** | Independent tests; numerical validation; permissions tests |
| **Reviewer** | Correctness, security, architecture, maintainability; severity taxonomy |
| **Documentation** | User, engineering, API, ops docs in the same increment |

## Capability state machine

```text
Backlog
  → Researching
  → Product definition
  → Architecture proposal
  → Waiting for approval          (Gate A and/or B as applicable)
  → Approved for implementation
  → In development                (Gate C)
  → Testing
  → Engineering validation        (Gate D)
  → Code review                   (Gate D)
  → Documentation
  → Waiting for completion approval (Gate E)
  → Accepted
  → Released
```

## Rules of engagement

1. **No implementation before approval** of the relevant gates.
2. **Research before calculation code**.
3. **Tests are independent** — Test Agent derives cases from approved requirements, not from “whatever the code does”.
4. **Scope freeze** during an increment; spillover → backlog.
5. **One capability → one PR** when possible.
6. **Blocker/major review findings** return work to development.
7. **Unresolved critical engineering assumptions** → Coordinator stops work.
8. **Human product owner** has final authority at Gates A, B, and E.

## Conflict resolution

| Conflict type | Resolution path |
|---------------|-----------------|
| Product vs Research methodology | Coordinator frames options; human decides (ED/PD) |
| Architect vs Developer shortcuts | Architecture wins unless ADR updated and approved |
| Test vs Developer tolerance dispute | Validation docs + Research; human if unresolved |
| Schedule vs correctness | Correctness wins; scope slips to backlog |

## Decision identifiers

| Prefix | Type |
|--------|------|
| PD-* | Product Decision |
| RD-* | Research Decision |
| AD-* | Architecture Decision |
| ED-* | Engineering Decision |
| SD-* | Security Decision |
| UD-* | User / product-owner Decision |

Confirmed decisions and assumptions are **always listed separately** in gate reports.
