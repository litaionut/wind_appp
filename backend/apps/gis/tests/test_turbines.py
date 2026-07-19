"""Turbine catalogue, positions, and distance tests."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.gis.models import (
    CoordinateReferenceSystem,
    ProjectCRS,
    ProjectCRSRole,
    TurbineModel,
)
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="turb_user", password="pass-turb-1")
    org = Organization.objects.create(name="Turb Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="Turb Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    crs = CoordinateReferenceSystem.objects.create(epsg_code=32633, name="UTM 33N")
    ProjectCRS.objects.create(project=project, crs=crs, role=ProjectCRSRole.HORIZONTAL)
    return user, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_catalogue_import_and_list(setup) -> None:
    user, _project = setup
    client = _auth(user)
    csv_body = (
        "manufacturer,model,hub_height_m,rotor_diameter_m,rated_power_kw\n"
        "Vestas,V150-4.2,105,150,4200\n"
    )
    response = client.post(
        reverse("turbine-catalogue-import"),
        {"file": SimpleUploadedFile("cat.csv", csv_body.encode(), content_type="text/csv")},
        format="multipart",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == 1
    assert TurbineModel.objects.filter(name="V150-4.2").exists()
    listed = client.get(reverse("turbine-models"))
    assert listed.status_code == status.HTTP_200_OK
    assert len(listed.json()) == 1


@pytest.mark.django_db
def test_position_create_and_pairwise_distance(setup) -> None:
    user, project = setup
    client = _auth(user)
    t1 = client.post(
        reverse("project-turbines", kwargs={"project_id": project.id}),
        {"label": "T1", "x": 0.0, "y": 0.0},
        format="json",
    )
    t2 = client.post(
        reverse("project-turbines", kwargs={"project_id": project.id}),
        {"label": "T2", "x": 300.0, "y": 400.0},
        format="json",
    )
    assert t1.status_code == status.HTTP_201_CREATED
    assert t2.status_code == status.HTTP_201_CREATED

    distances = client.get(
        reverse("project-turbine-distances", kwargs={"project_id": project.id})
    )
    assert distances.status_code == status.HTTP_200_OK
    assert distances.json()["count"] == 1
    pair = distances.json()["pairs"][0]
    assert pair["distance_m"] == pytest.approx(500.0)
    assert pair["unit"] == "m"
    assert pair["method"] == "planar_metres"


@pytest.mark.django_db
def test_positions_csv_import(setup) -> None:
    user, project = setup
    client = _auth(user)
    csv_body = "label,x,y,z\nA1,10,20,\nA2,30,40,5\n"
    response = client.post(
        reverse("project-turbines-import", kwargs={"project_id": project.id}),
        {
            "file": SimpleUploadedFile(
                "pos.csv", csv_body.encode(), content_type="text/csv"
            )
        },
        format="multipart",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["created"] == 2
