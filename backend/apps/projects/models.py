"""Project and project membership models."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.organizations.models import Organization


class ProjectRole(models.TextChoices):
    PROJECT_ADMIN = "project_admin", "Project admin"
    PROJECT_ENGINEER = "project_engineer", "Project engineer"
    PROJECT_VIEWER = "project_viewer", "Project viewer"


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="uniq_organization_project_slug",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name) or "project"
        candidate = base
        suffix = 2
        qs = Project.objects.filter(organization=self.organization)
        while qs.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate


class ProjectMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=32,
        choices=ProjectRole.choices,
        default=ProjectRole.PROJECT_VIEWER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="uniq_project_user_membership",
            )
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.project} ({self.role})"
