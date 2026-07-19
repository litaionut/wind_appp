# Numerical Tolerances

**Document ID:** VAL-003  
**Status:** Proposed defaults  
**Last updated:** 2026-07-19

| Quantity class | Default absolute tol | Default relative tol | Notes |
|----------------|----------------------|----------------------|-------|
| Dimensionless ratios | 1e-12 | 1e-9 | Exact arithmetic paths |
| Distances (m) | 1e-6 m | 1e-9 | CRS-dependent; tighten/loosen per method |
| Energy (MWh) | method-specific | 1e-6 | Set per method version |
| Wind speed (m/s) | 1e-6 | 1e-8 | |
| Angles (deg) | 1e-6 | — | Sector edges documented |

Each calculation method **must** override with method-specific tolerances in its research/validation brief.
