"""Environment module tests."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.gis.models import TurbineManufacturer, TurbineModel, TurbinePosition
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="env_user", password="pass-env-1")
    org = Organization.objects.create(name="Env Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Env Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    mfr = TurbineManufacturer.objects.create(name="OEM-E")
    model = TurbineModel.objects.create(
        manufacturer=mfr,
        name="T-E",
        hub_height_m=100,
        rotor_diameter_m=120,
        rated_power_kw=3000,
    )
    TurbinePosition.objects.create(project=project, label="T1", x=0, y=0, turbine_model=model)
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_noise_and_shadow(setup) -> None:
    user, project = setup
    client = _auth(user)

    rec = client.post(
        reverse("environment-receptors", kwargs={"project_id": project.id}),
        {"name": "House A", "x": 800, "y": 0},
        format="json",
    )
    assert rec.status_code == status.HTTP_201_CREATED

    noise = client.post(
        reverse("environment-noise-run", kwargs={"project_id": project.id}),
        {"source_lw_db": 105},
        format="json",
    )
    assert noise.status_code == status.HTTP_201_CREATED
    assert noise.json()["method_version"] == "noise_spreading_v1"
    assert noise.json()["receptors"][0]["level_db"] is not None

    shadow = client.post(
        reverse("environment-shadow-run", kwargs={"project_id": project.id}),
        {},
        format="json",
    )
    assert shadow.status_code == status.HTTP_201_CREATED
    assert shadow.json()["method_version"] == "shadow_distance_v1"
