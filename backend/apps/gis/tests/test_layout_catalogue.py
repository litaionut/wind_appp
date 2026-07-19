"""Catalogue create + Ct curve tests."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="layout_user", password="pass-layout-1")
    org = Organization.objects.create(name="Layout Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Layout Project", created_by=user)
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
def test_create_model_and_ct_curve(setup) -> None:
    user, project = setup
    client = _auth(user)

    model = client.post(
        reverse("turbine-models"),
        {
            "manufacturer_name_write": "OEM-L",
            "name": "L-120",
            "hub_height_m": 100,
            "rotor_diameter_m": 120,
            "rated_power_kw": 3000,
        },
        format="json",
    )
    assert model.status_code == status.HTTP_201_CREATED, model.json()
    model_id = model.json()["id"]

    ct = client.post(
        reverse("ct-curves"),
        {"turbine_model": model_id, "name": "L-120 Ct", "air_density_ref_kg_m3": 1.225},
        format="json",
    )
    assert ct.status_code == status.HTTP_201_CREATED
    curve_id = ct.json()["id"]

    imported = client.post(
        reverse("ct-curve-import", kwargs={"curve_id": curve_id}),
        {
            "file": SimpleUploadedFile(
                "ct.csv",
                b"ws_m_s,ct\n0,0\n5,0.8\n10,0.7\n25,0.05\n",
                content_type="text/csv",
            )
        },
        format="multipart",
    )
    assert imported.status_code == status.HTTP_200_OK
    assert imported.json()["points"] == 4

    turbine = client.post(
        reverse("project-turbines", kwargs={"project_id": project.id}),
        {"label": "T1", "x": 100, "y": 200, "turbine_model": model_id},
        format="json",
    )
    assert turbine.status_code == status.HTTP_201_CREATED
