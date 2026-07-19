"""File API tests."""

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.files.models import FileObject
from apps.organizations.models import Organization, OrganizationMembership, OrganizationRole
from apps.projects.models import Project, ProjectMembership, ProjectRole


@pytest.fixture
def setup(db):
    user = User.objects.create_user(username="file_user", password="pass-file-1")
    org = Organization.objects.create(name="File Org", created_by=user)
    OrganizationMembership.objects.create(
        organization=org, user=user, role=OrganizationRole.ORG_ADMIN
    )
    project = Project.objects.create(organization=org, name="File Project", created_by=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectRole.PROJECT_ADMIN
    )
    return user, org, project


def _auth(user: User) -> APIClient:
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.mark.django_db
def test_upload_list_download(setup) -> None:
    user, _org, project = setup
    client = _auth(user)
    upload = SimpleUploadedFile("notes.txt", b"hello wind", content_type="text/plain")
    created = client.post(
        reverse("project-files", kwargs={"project_id": project.id}),
        {"file": upload},
        format="multipart",
    )
    assert created.status_code == status.HTTP_201_CREATED
    file_id = created.json()["id"]
    assert FileObject.objects.filter(id=file_id).exists()

    listed = client.get(reverse("project-files", kwargs={"project_id": project.id}))
    assert listed.status_code == status.HTTP_200_OK
    assert len(listed.json()) == 1

    download = client.get(reverse("file-download", kwargs={"file_id": file_id}))
    assert download.status_code == status.HTTP_200_OK
    assert download.getvalue() == b"hello wind"


@pytest.mark.django_db
def test_outsider_cannot_access_file(setup) -> None:
    user, _org, project = setup
    outsider = User.objects.create_user(username="file_out", password="pass-out-1")
    client = _auth(user)
    upload = SimpleUploadedFile("secret.txt", b"secret", content_type="text/plain")
    created = client.post(
        reverse("project-files", kwargs={"project_id": project.id}),
        {"file": upload},
        format="multipart",
    )
    file_id = created.json()["id"]
    out_client = _auth(outsider)
    response = out_client.get(reverse("file-detail", kwargs={"file_id": file_id}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
