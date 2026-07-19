"""R6–R9 stub API smoke tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="r69_user", password="pass-r69-1")
    org = Organization.objects.create(name="R69 Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="R69 Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_suitability_ops_financial_hybrid(setup) -> None:
    user, project = setup
    client = _auth(user)
    pid = {"project_id": project.id}

    iec = client.post(
        reverse("suitability-iec-class", kwargs=pid),
        {"vave_m_s": 8.0, "i_ref": 0.16},
        format="json",
    )
    assert iec.status_code == status.HTTP_201_CREATED
    assert "IEC" in iec.json()["label"]

    terrain = client.post(
        reverse("suitability-terrain", kwargs=pid),
        {"elevation_std_m": 20, "slope_deg": 5},
        format="json",
    )
    assert terrain.status_code == status.HTTP_201_CREATED

    kpi = client.post(
        reverse("operations-availability-kpi", kwargs=pid),
        {
            "period_hours": 8760,
            "downtime_hours": 438,
            "energy_produced_mwh": 90000,
            "energy_expected_mwh": 100000,
        },
        format="json",
    )
    assert kpi.status_code == status.HTTP_201_CREATED
    assert kpi.json()["availability"] == pytest.approx(0.95)

    el = client.post(
        reverse("financial-electrical-loss", kwargs=pid),
        {"gross_aep_mwh": 100000, "cable_loss_fraction": 0.02, "transformer_loss_fraction": 0.01},
        format="json",
    )
    assert el.status_code == status.HTTP_201_CREATED
    assert el.json()["net_aep_mwh"] == pytest.approx(97000.0)

    fin = client.post(
        reverse("financial-lcoe-npv", kwargs=pid),
        {
            "annual_energy_mwh": 100000,
            "capex": 120_000_000,
            "opex_annual": 2_000_000,
            "price_per_mwh": 50,
        },
        format="json",
    )
    assert fin.status_code == status.HTTP_201_CREATED
    assert fin.json()["lcoe_per_mwh"] is not None

    pv = client.post(
        reverse("hybrid-pv-yield", kwargs=pid),
        {"capacity_mw": 50, "capacity_factor": 0.2},
        format="json",
    )
    assert pv.status_code == status.HTTP_201_CREATED
    assert pv.json()["annual_energy_mwh"] == pytest.approx(87600.0)

    curt = client.post(
        reverse("hybrid-curtailment", kwargs=pid),
        {"wind_mw": [40, 60], "solar_mw": [20, 30], "grid_limit_mw": 50},
        format="json",
    )
    assert curt.status_code == status.HTTP_201_CREATED
    assert curt.json()["energy_curtailed_mwh"] == pytest.approx(50.0)
