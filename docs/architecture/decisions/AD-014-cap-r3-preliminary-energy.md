# AD-014 — CAP-R3 Preliminary Energy

**Status:** Approved (UD-008)

1. `PowerCurve` linked to `TurbineModel`: points (ws_m_s, power_kw), air density ref.
2. CSV import `ws_m_s,power_kw`.
3. Simple Weibull or discrete frequency distribution input for gross energy.
4. Gross AEP = sum(P(v) * hours) with linear interpolation on power curve.
5. Per-turbine free-flow energy; plant sum; optional constant wake loss factor (not a physical wake model).
6. Method version `gross_energy_v1` registered in calculation methods.
