"""Project boundaries and exclusion zones (GeoJSON polygons)."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class BoundaryKind(models.TextChoices):
    PROJECT_BOUNDARY = "project_boundary", "Project boundary"
    EXCLUSION_ZONE = "exclusion_zone", "Exclusion zone"


class ProjectBoundary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="boundaries")
    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=32, choices=BoundaryKind.choices)
    # GeoJSON Polygon/MultiPolygon geometry object
    geometry = models.JSONField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="boundaries_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "project boundaries"

    def __str__(self) -> str:
        return f"{self.name} ({self.kind})"
