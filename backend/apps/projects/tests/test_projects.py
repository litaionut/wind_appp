"""Tests for project API."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_a(db) -> User:
    return User.objects.create_user(username="proj_a", password="pass-a-12345")


@pytest.fixture
def user_b(db) -> User:
    return User.objects.create_user(username="proj_b", password="pass-b-12345")


@pytest.fixture
def org(user_a: User) -> Organization:
    organization = Organization.objects.create(name="Proj Org", created_by=user_a)
    OrganizationMembership.objects.create(
        organization=organization,
        user=user_a,
        role=OrganizationRole.ORG_ADMIN,
    )
    return organization


def _auth(client: APIClient, user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_org_member_can_create_project(
    api_client: APIClient, user_a: User, org: Organization
) -> None:
    client = _auth(api_client, user_a)
    response = client.post(
        reverse("organization-projects", kwargs={"org_id": org.id}),
        {"name": "Site Alpha"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["slug"] == "site-alpha"
    assert ProjectMembership.objects.filter(
        project_id=response.json()["id"],
        user=user_a,
        role=ProjectRole.PROJECT_ADMIN,
    ).exists()


@pytest.mark.django_db
def test_non_org_member_cannot_create_project(
    api_client: APIClient, user_b: User, org: Organization
) -> None:
    client = _auth(api_client, user_b)
    response = client.post(
        reverse("organization-projects", kwargs={"org_id": org.id}),
        {"name": "Forbidden"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_only_member_projects(
    api_client: APIClient, user_a: User, user_b: User, org: Organization
) -> None:
    OrganizationMembership.objects.create(
        organization=org, user=user_b, role=OrganizationRole.ORG_MEMBER
    )
    p1 = Project.objects.create(organization=org, name="P1", created_by=user_a)
    p2 = Project.objects.create(organization=org, name="P2", created_by=user_b)
    ProjectMembership.objects.create(
        project=p1, user=user_a, role=ProjectRole.PROJECT_ADMIN
    )
    ProjectMembership.objects.create(
        project=p2, user=user_b, role=ProjectRole.PROJECT_ADMIN
    )

    client = _auth(api_client, user_a)
    response = client.get(reverse("organization-projects", kwargs={"org_id": org.id}))
    assert response.status_code == status.HTTP_200_OK
    ids = {item["id"] for item in response.json()}
    assert ids == {str(p1.id)}


@pytest.mark.django_db
def test_non_member_cannot_retrieve_project(
    api_client: APIClient, user_a: User, user_b: User, org: Organization
) -> None:
    project = Project.objects.create(organization=org, name="Hidden", created_by=user_a)
    ProjectMembership.objects.create(
        project=project, user=user_a, role=ProjectRole.PROJECT_ADMIN
    )
    client = _auth(api_client, user_b)
    response = client.get(reverse("project-detail", kwargs={"project_id": project.id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_project_admin_can_patch(
    api_client: APIClient, user_a: User, org: Organization
) -> None:
    project = Project.objects.create(organization=org, name="Editable", created_by=user_a)
    ProjectMembership.objects.create(
        project=project, user=user_a, role=ProjectRole.PROJECT_ADMIN
    )
    client = _auth(api_client, user_a)
    response = client.patch(
        reverse("project-detail", kwargs={"project_id": project.id}),
        {"name": "Renamed"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Renamed"
