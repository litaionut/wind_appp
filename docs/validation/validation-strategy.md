# Validation Strategy

**Document ID:** VAL-001  
**Status:** Proposed  
**Last updated:** 2026-07-19

---

## Engineering validation sources (priority order)

1. Hand-calculated examples with documented steps  
2. Published examples from standards/guidance (legally citable)  
3. Independently created reference calculations  
4. Approved benchmark datasets  
5. Previous validated platform results (regression)

## R0 note

R0 has **no physical engineering calculations**. Validation focuses on:

- Security isolation
- Audit completeness
- Calculation-run metadata integrity
- Reproducibility of stub/method registry behaviour

Numerical engineering validation begins with R1 spacing / R2 METEO methods.
