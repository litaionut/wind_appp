# Calculation Framework Concept

**Document ID:** ARCH-005  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Purpose

Provide a common execution and audit model for all engineering calculations so that results are **deterministic** (same inputs → same outputs), **reproducible**, **traceable**, **versioned**, and **testable without the UI**.

## Method registry

Every calculation method is registered as:

```text
{method_id}_{version}
```

Examples:

- `spacing_directional_v1`
- `wind_rose_v1`
- `air_density_v1`
- `gross_energy_v1`
- `wake_model_initial_v1`

Registry fields (conceptual):

| Field | Purpose |
|-------|---------|
| method_id | Stable identifier |
| version | Monotonic method version |
| title / description | Human-readable |
| input_schema | JSON Schema or equivalent |
| output_schema | JSON Schema or equivalent |
| units_map | Explicit units for engineering fields |
| assumptions_doc_ref | Link to methodology docs |
| status | experimental \| approved_default \| deprecated |
| feature_flag | Optional gate for experimental methods |

**Rule:** Changing an equation or default assumption that may change results **requires a new method version**. Historical runs keep their original method version.

## Calculation run lifecycle

```text
queued → running → succeeded
                 → failed
                 → cancelled
```

Each run records:

- project, organization
- calculation type
- method id + version
- application version
- input files / entities / parameters / assumptions
- execution status + timestamps
- results, warnings, errors
- generated artifacts
- validation status
- actor (user)

## Units policy

- Every engineering value has an explicit unit.
- Prefer a centralized unit library / conversion service (selection in implementation ADR).
- No undocumented implicit units in APIs or DB fields.
- Persist either canonical SI + display unit, or quantity objects serialized with unit — decision at method design time, consistent platform-wide (ED-* later).

## Determinism rules

- Pure functions for core math where possible
- Seed recorded if stochastic methods ever appear (default: avoid stochastic calcs)
- Timezone-normalized timestamps for time-series inputs
- Float tolerances documented in `docs/validation/numerical-tolerances.md`

## Execution model

| Phase | Executor |
|-------|----------|
| R0 | Synchronous stub / registry + run records (no heavy compute) |
| R2+ | Background workers for long imports/calcs |
| Always | Domain logic independent of HTTP layer |

## Validation status

Runs may carry:

- `not_validated`
- `smoke_ok`
- `benchmark_ok`
- `failed_validation`

A run that “executed without error” is **not** automatically validated.

## Experimental methods

- Protected by feature flags
- Must not become default without explicit ED/PD approval
