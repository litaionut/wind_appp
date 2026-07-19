"""Report artifact model."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.calculations.models import CalculationRun
from apps.files.models import FileObject
from apps.organizations.models import Organization
from apps.projects.models import Project


class ReportArtifact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="report_artifacts"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="report_artifacts"
    )
    calculation_run = models.ForeignKey(
        CalculationRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_artifacts",
    )
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128, default="application/json")
    file = models.ForeignKey(
        FileObject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_artifacts",
    )
    summary = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_artifacts_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
