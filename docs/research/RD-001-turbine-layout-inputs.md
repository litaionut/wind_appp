# RD-001 — Turbine / layout / curve inputs (research)

**Status:** Accepted for MVP layout UI (UD-008)  
**Date:** 2026-07-19  
**Research agent:** Coordinator-assisted

## Summary

Catalogue, positions, and power curves exist; **Ct curves do not**. Jensen wake uses constant Ct=0.8.

## MVP required inputs

| Domain | Fields |
|--------|--------|
| Manufacturer | `name` |
| Model | `manufacturer`, `name`, `hub_height_m>0`, `rotor_diameter_m>0`, `rated_power_kw>0` |
| Position | `label` (unique/project), `x`, `y`, `turbine_model` (required in UI) |
| Power curve | `ws_m_s`, `power_kw`, `air_density_ref_kg_m3` |
| Ct curve | `ws_m_s`, `ct` (0…1) — **new** |

## File schemas

- Catalogue: `manufacturer,model,hub_height_m,rotor_diameter_m,rated_power_kw`
- Positions: `label,x,y[,z][,manufacturer,model]` (manufacturer+model preferred)
- Power: `ws_m_s,power_kw`
- Ct: `ws_m_s,ct`

## Risks

Missing Ct → non-bankable wakes; density/HH stored but not fully used in AEP; model name-only CSV collisions.
