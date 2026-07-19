"""Preliminary energy tests."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.gis.models import TurbineManufacturer, TurbineModel, TurbinePosition
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="energy_user", password="pass-energy-1")
    org = Organization.objects.create(name="Energy Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Energy Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    mfr = TurbineManufacturer.objects.create(name="OEM")
    model = TurbineModel.objects.create(
        manufacturer=mfr,
        name="T-100",
        hub_height_m=100,
        rotor_diameter_m=120,
        rated_power_kw=3000,
    )
    TurbinePosition.objects.create(project=project, label="T1", x=0, y=0, turbine_model=model)
    TurbinePosition.objects.create(project=project, label="T2", x=500, y=0, turbine_model=model)
    return user, project, model


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_power_curve_and_gross_aep(setup) -> None:
    user, project, model = setup
    client = _auth(user)

    curve = client.post(
        reverse("power-curves"),
        {
            "turbine_model": str(model.id),
            "name": "T-100 IEC",
            "air_density_ref_kg_m3": 1.225,
        },
        format="json",
    )
    assert curve.status_code == status.HTTP_201_CREATED
    curve_id = curve.json()["id"]

    csv_body = "ws_m_s,power_kw\n0,0\n5,500\n10,2000\n15,3000\n25,3000\n"
    imported = client.post(
        reverse("power-curve-import", kwargs={"curve_id": curve_id}),
        {
            "file": SimpleUploadedFile(
                "pc.csv", csv_body.encode(), content_type="text/csv"
            )
        },
        format="multipart",
    )
    assert imported.status_code == status.HTTP_200_OK
    assert imported.json()["points"] == 5

    # 8760 h at 10 m/s → 2000 kW * 8760 = 17,520,000 kWh = 17520 MWh per turbine
    assessment = client.post(
        reverse("project-energy-assessments", kwargs={"project_id": project.id}),
        {
            "name": "P50 gross",
            "power_curve": curve_id,
            "wind_distribution": [{"ws_m_s": 10, "hours": 8760}],
            "wake_loss_fraction": 0.1,
        },
        format="json",
    )
    assert assessment.status_code == status.HTTP_201_CREATED
    results = assessment.json()["results"]
    assert results["method_version"] == "gross_energy_v1"
    assert results["per_turbine_gross_aep_mwh"] == pytest.approx(17520.0)
    assert results["per_turbine_net_aep_mwh"] == pytest.approx(15768.0)
    assert results["turbine_count"] == 2
    assert results["plant_net_aep_mwh"] == pytest.approx(31536.0)
