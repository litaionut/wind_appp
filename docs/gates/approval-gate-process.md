# Approval Gate Process

**Document ID:** GT-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Gate summary

| Gate | Name | Presenters | Human decision |
|------|------|------------|----------------|
| **A** | Problem & research approval | Product + Research (+ Coordinator) | Approve / approve with conditions / reject / defer |
| **B** | Technical design approval | Architect | Same |
| **C** | Implementation | Developer | Coordinator checkpoints; human optional for risky increments |
| **D** | Independent testing & review | Test + Reviewer | Return to dev if blocker/major |
| **E** | Completion approval | Coordinator | Approve merge/release / conditions / reject |

## Gate A — Problem and research

Must present: problem, scope, standards, methodology, major decisions, assumptions, alternatives, risks.

**No architecture deep-dive required yet**, but known constraints may be listed.

## Gate B — Technical design

Must present: domain model, system design, API, calculation design, data/file flows, security impact, implementation increments, test strategy, rollback strategy.

## Gate C — Implementation

Developer submits: source, migrations, tests written during development, implementation notes, files changed, risks.

## Gate D — Testing and review

- Test Agent: independent suite + numerical checks with documented tolerances
- Reviewer: blocker / major / minor / recommendation
- Blocker & major must be resolved before Gate E

## Gate E — Completion

Coordinator presents completion report (section 15 format). No merge/release without recorded approval.

## Required report formats

- Approval gates → section 14 template (`docs/gates/approval-report-template.md`)
- Completion → section 15 template (`docs/gates/completion-report-template.md`)

## Recording decisions

Decisions are appended to `docs/architecture/decisions/` (ADRs) or `docs/product/decisions-log.md` with ID, date, status, and owner.
