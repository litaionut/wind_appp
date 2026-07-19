# AD-016 — Layout UI + Ct curves + catalogue CRUD

**Status:** Approved (UD-008 / owner “hai sa incepem cu layout-ul”)  
**Date:** 2026-07-19  
**Depends on:** RD-001, AD-011, AD-014, UD-002

## Decision

1. **SPA Layout page** per project: list turbines, CSV import, Leaflet map (planar x/y via `L.CRS.Simple`), edit coordinates, assign model.
2. **Catalogue CRUD API:** create manufacturer + model with positive HH/RD/rated validation; keep CSV import.
3. **CtCurve** model + CSV import (`ws_m_s,ct`), linked to `TurbineModel`; create flow in UI with power + Ct.
4. Position import accepts optional `manufacturer,model` (preferred) while keeping `model` name for compatibility.
5. Map does **not** require WGS84; coordinates shown in project storage CRS (metres or stored units).

## Out of scope this increment

Interactive draw of boundaries; bankable wake; density correction; hub-height shear.
