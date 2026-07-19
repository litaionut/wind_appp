"""Tests for audit event recording and read APIs."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.audit.models import AuditEvent
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_user(username="audit_admin", password="pass-audit-1")


@pytest.fixture
def member_user(db) -> User:
    return User.objects.create_user(username="audit_member", password="pass-audit-2")


def _auth(client: APIClient, user: User) -> APIClient:
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_organization_create_writes_audit(api_client: APIClient, admin_user: User) -> None:
    client = _auth(api_client, admin_user)
    response = client.post(
        reverse("organization-list"),
        {"name": "Audited Org"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert AuditEvent.objects.filter(
        action="organization.created",
        organization_id=response.json()["id"],
        actor=admin_user,
    ).exists()


@pytest.mark.django_db
def test_org_admin_can_list_audit_events(
    api_client: APIClient, admin_user: User, member_user: User
) -> None:
    org = Organization.objects.create(name="List Org", created_by=admin_user)
    OrganizationMembership.objects.create(
        organization=org, user=admin_user, role=OrganizationRole.ORG_ADMIN
    )
    OrganizationMembership.objects.create(
        organization=org, user=member_user, role=OrganizationRole.ORG_MEMBER
    )
    AuditEvent.objects.create(
        action="organization.created",
        actor=admin_user,
        organization=org,
        entity_type="organization",
        entity_id=str(org.id),
    )

    admin_client = _auth(api_client, admin_user)
    ok = admin_client.get(reverse("organization-audit-events", kwargs={"org_id": org.id}))
    assert ok.status_code == status.HTTP_200_OK
    assert len(ok.json()) == 1

    member_client = APIClient()
    member_client = _auth(member_client, member_user)
    denied = member_client.get(
        reverse("organization-audit-events", kwargs={"org_id": org.id})
    )
    assert denied.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_project_create_writes_audit(api_client: APIClient, admin_user: User) -> None:
    org = Organization.objects.create(name="Proj Audit Org", created_by=admin_user)
    OrganizationMembership.objects.create(
        organization=org, user=admin_user, role=OrganizationRole.ORG_ADMIN
    )
    client = _auth(api_client, admin_user)
    response = client.post(
        reverse("organization-projects", kwargs={"org_id": org.id}),
        {"name": "Audited Project"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert AuditEvent.objects.filter(
        action="project.created",
        project_id=response.json()["id"],
        actor=admin_user,
    ).exists()


@pytest.mark.django_db
def test_login_writes_audit(api_client: APIClient, admin_user: User) -> None:
    response = api_client.post(
        reverse("auth-login"),
        {"username": "audit_admin", "password": "pass-audit-1"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert AuditEvent.objects.filter(action="auth.login", actor=admin_user).exists()


@pytest.mark.django_db
def test_project_admin_can_list_project_audit(
    api_client: APIClient, admin_user: User
) -> None:
    org = Organization.objects.create(name="POrg", created_by=admin_user)
    OrganizationMembership.objects.create(
        organization=org, user=admin_user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="P", created_by=admin_user)
    ProjectMembership.objects.create(
        project=project, user=admin_user, role=ProjectRole.PROJECT_ADMIN
    )
    AuditEvent.objects.create(
        action="project.created",
        actor=admin_user,
        organization=org,
        project=project,
    )
    client = _auth(api_client, admin_user)
    response = client.get(
        reverse("project-audit-events", kwargs={"project_id": project.id})
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["action"] == "project.created"
