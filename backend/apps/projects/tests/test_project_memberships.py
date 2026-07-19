"""Tests for project membership management API."""

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
def admin_user(db) -> User:
    return User.objects.create_user(username="padmin", password="pass-padmin-1")


@pytest.fixture
def org_member(db) -> User:
    return User.objects.create_user(username="pmember", password="pass-pmember-1")


@pytest.fixture
def setup(admin_user: User, org_member: User):
    org = Organization.objects.create(name="PM Org", created_by=admin_user)
    OrganizationMembership.objects.create(
        organization=org, user=admin_user, role=OrganizationRole.ORG_ADMIN
    )
    OrganizationMembership.objects.create(
        organization=org, user=org_member, role=OrganizationRole.ORG_MEMBER
    )
    project = Project.objects.create(organization=org, name="PM Project", created_by=admin_user)
    admin_membership = ProjectMembership.objects.create(
        project=project, user=admin_user, role=ProjectRole.PROJECT_ADMIN
    )
    return org, project, admin_membership


def _auth(client: APIClient, user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_add_org_member_to_project(api_client, admin_user, org_member, setup) -> None:
    _org, project, _ = setup
    client = _auth(api_client, admin_user)
    response = client.post(
        reverse("project-members", kwargs={"project_id": project.id}),
        {"username": "pmember", "role": "project_engineer"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["role"] == "project_engineer"


@pytest.mark.django_db
def test_cannot_add_non_org_member(api_client, admin_user, setup) -> None:
    User.objects.create_user(username="stranger", password="pass-stranger-1")
    _org, project, _ = setup
    client = _auth(api_client, admin_user)
    response = client.post(
        reverse("project-members", kwargs={"project_id": project.id}),
        {"username": "stranger", "role": "project_viewer"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_cannot_remove_last_project_admin(api_client, admin_user, setup) -> None:
    _org, project, membership = setup
    client = _auth(api_client, admin_user)
    response = client.delete(
        reverse(
            "project-member-detail",
            kwargs={"project_id": project.id, "membership_id": membership.id},
        )
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
