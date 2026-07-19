"""Electrical loss and financial metric stubs."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class FinancialCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="financial_cases"
    )
    name = models.CharField(max_length=255)
    method_version = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict, blank=True)
    results = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


def electrical_loss_stub(
    *,
    gross_aep_mwh: float,
    cable_loss_fraction: float = 0.02,
    transformer_loss_fraction: float = 0.01,
) -> dict:
    """Apply constant electrical losses. Version electrical_loss_v1."""
    total_frac = max(0.0, min(0.5, cable_loss_fraction + transformer_loss_fraction))
    net = gross_aep_mwh * (1.0 - total_frac)
    return {
        "method_version": "electrical_loss_v1",
        "gross_aep_mwh": gross_aep_mwh,
        "cable_loss_fraction": cable_loss_fraction,
        "transformer_loss_fraction": transformer_loss_fraction,
        "total_electrical_loss_fraction": total_frac,
        "net_aep_mwh": net,
        "note": "Constant-loss stub — cable routing deferred",
    }


def lcoe_npv_stub(
    *,
    annual_energy_mwh: float,
    capex: float,
    opex_annual: float,
    lifetime_years: int = 25,
    discount_rate: float = 0.07,
    price_per_mwh: float = 50.0,
) -> dict:
    """Simple LCOE and NPV. Version lcoe_npv_v1."""
    if lifetime_years < 1:
        lifetime_years = 1
    # Levelized cost of energy (simplified annuity)
    if discount_rate <= 0:
        crf = 1.0 / lifetime_years
    else:
        r = discount_rate
        n = lifetime_years
        crf = (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    annual_cost = capex * crf + opex_annual
    lcoe = annual_cost / annual_energy_mwh if annual_energy_mwh > 0 else None

    npv = -capex
    for year in range(1, lifetime_years + 1):
        cash = annual_energy_mwh * price_per_mwh - opex_annual
        npv += cash / ((1 + discount_rate) ** year)

    # IRR via bisection on NPV=0 (stub range)
    irr = None
    lo, hi = -0.5, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        val = -capex
        for year in range(1, lifetime_years + 1):
            cash = annual_energy_mwh * price_per_mwh - opex_annual
            val += cash / ((1 + mid) ** year)
        if val > 0:
            lo = mid
        else:
            hi = mid
    irr = (lo + hi) / 2.0

    return {
        "method_version": "lcoe_npv_v1",
        "lcoe_per_mwh": lcoe,
        "npv": npv,
        "irr": irr,
        "lifetime_years": lifetime_years,
        "discount_rate": discount_rate,
        "currency_note": "Currency-agnostic numeric inputs",
    }
