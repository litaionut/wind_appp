"""R4 advanced energy tests."""

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
    user = User.objects.create_user(username="adv_energy", password="pass-adv-1")
    org = Organization.objects.create(name="Adv Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Adv Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    mfr = TurbineManufacturer.objects.create(name="OEM-A")
    model = TurbineModel.objects.create(
        manufacturer=mfr,
        name="T-A",
        hub_height_m=100,
        rotor_diameter_m=120,
        rated_power_kw=3000,
    )
    TurbinePosition.objects.create(project=project, label="T1", x=0, y=0, turbine_model=model)
    TurbinePosition.objects.create(project=project, label="T2", x=600, y=0, turbine_model=model)
    return user, project, model


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_mcp_wake_uncertainty(setup) -> None:
    user, project, model = setup
    client = _auth(user)

    mcp = client.post(
        reverse("energy-mcp-linear", kwargs={"project_id": project.id}),
        {"target_means": [5.0, 6.0, 7.0], "reference_means": [4.5, 5.5, 6.5]},
        format="json",
    )
    assert mcp.status_code == status.HTTP_200_OK
    assert mcp.json()["method_version"] == "mcp_linear_v1"
    assert mcp.json()["r_squared"] > 0.99

    wake = client.post(
        reverse("energy-wake-jensen", kwargs={"project_id": project.id}),
        {"wind_direction_deg": 90},
        format="json",
    )
    assert wake.status_code == status.HTTP_200_OK
    assert wake.json()["method_version"] == "wake_jensen_initial_v1"
    assert 0 <= wake.json()["wake_loss_fraction"] <= 0.5

    curve = client.post(
        reverse("power-curves"),
        {"turbine_model": str(model.id), "name": "PC", "air_density_ref_kg_m3": 1.225},
        format="json",
    )
    curve_id = curve.json()["id"]
    client.post(
        reverse("power-curve-import", kwargs={"curve_id": curve_id}),
        {
            "file": SimpleUploadedFile(
                "pc.csv",
                b"ws_m_s,power_kw\n0,0\n10,2000\n25,3000\n",
                content_type="text/csv",
            )
        },
        format="multipart",
    )
    assessment = client.post(
        reverse("project-energy-assessments", kwargs={"project_id": project.id}),
        {
            "name": "AEP",
            "power_curve": curve_id,
            "wind_distribution": [{"ws_m_s": 10, "hours": 8760}],
            "wake_loss_fraction": 0.0,
        },
        format="json",
    )
    assessment_id = assessment.json()["id"]
    unc = client.post(
        reverse(
            "energy-uncertainty",
            kwargs={"project_id": project.id, "assessment_id": assessment_id},
        ),
        {"combined_uncertainty": 0.12},
        format="json",
    )
    assert unc.status_code == status.HTTP_200_OK
    body = unc.json()
    assert body["method_version"] == "uncertainty_normal_v1"
    assert body["p90_aep_mwh"] < body["p50_aep_mwh"]
