"""File metadata model."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.organizations.models import Organization
from apps.projects.models import Project


class FileObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="files"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    original_name = models.CharField(max_length=512)
    content_type = models.CharField(max_length=255, blank=True, default="application/octet-stream")
    size_bytes = models.PositiveBigIntegerField(default=0)
    checksum_sha256 = models.CharField(max_length=64)
    storage_key = models.CharField(max_length=1024, unique=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.original_name
