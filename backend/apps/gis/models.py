"""CRS catalogue and project CRS assignment."""

from __future__ import annotations

import uuid

from django.db import models

from apps.projects.models import Project


class CoordinateReferenceSystem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    epsg_code = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    auth_name = models.CharField(max_length=64, default="EPSG")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["epsg_code"]
        verbose_name = "Coordinate reference system"
        verbose_name_plural = "Coordinate reference systems"

    def __str__(self) -> str:
        return f"EPSG:{self.epsg_code} ({self.name})"


class ProjectCRSRole(models.TextChoices):
    HORIZONTAL = "horizontal", "Horizontal"
    DISPLAY = "display", "Display"


class ProjectCRS(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="crs_links")
    crs = models.ForeignKey(
        CoordinateReferenceSystem, on_delete=models.PROTECT, related_name="project_links"
    )
    role = models.CharField(
        max_length=32, choices=ProjectCRSRole.choices, default=ProjectCRSRole.HORIZONTAL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "role"],
                name="uniq_project_crs_role",
            )
        ]

    def __str__(self) -> str:
        return f"{self.project} [{self.role}] → {self.crs}"
