"""Calculation method registry, runs, and logs."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.organizations.models import Organization
from apps.projects.models import Project


class MethodStatus(models.TextChoices):
    EXPERIMENTAL = "experimental", "Experimental"
    APPROVED_DEFAULT = "approved_default", "Approved default"
    DEPRECATED = "deprecated", "Deprecated"


class CalculationMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    method_id = models.CharField(max_length=128)
    version = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=32,
        choices=MethodStatus.choices,
        default=MethodStatus.EXPERIMENTAL,
    )
    input_schema = models.JSONField(default=dict, blank=True)
    output_schema = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["method_id", "version"]
        constraints = [
            models.UniqueConstraint(
                fields=["method_id", "version"],
                name="uniq_calculation_method_id_version",
            )
        ]

    @property
    def registry_key(self) -> str:
        return f"{self.method_id}_{self.version}"

    def __str__(self) -> str:
        return self.registry_key


class RunStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class ValidationStatus(models.TextChoices):
    NOT_VALIDATED = "not_validated", "Not validated"
    SMOKE_OK = "smoke_ok", "Smoke OK"
    BENCHMARK_OK = "benchmark_ok", "Benchmark OK"
    FAILED_VALIDATION = "failed_validation", "Failed validation"


class CalculationRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="calculation_runs"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="calculation_runs"
    )
    method = models.ForeignKey(
        CalculationMethod, on_delete=models.PROTECT, related_name="runs"
    )
    calculation_type = models.CharField(max_length=128)
    application_version = models.CharField(max_length=32, default="0.1.0")
    input_data_version = models.CharField(max_length=64, blank=True, default="")
    parameters = models.JSONField(default=dict, blank=True)
    assumptions = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=32, choices=RunStatus.choices, default=RunStatus.QUEUED
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calculation_runs_created",
    )
    results = models.JSONField(default=dict, blank=True)
    warnings = models.JSONField(default=list, blank=True)
    errors = models.JSONField(default=list, blank=True)
    validation_status = models.CharField(
        max_length=32,
        choices=ValidationStatus.choices,
        default=ValidationStatus.NOT_VALIDATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.calculation_type}:{self.id}"


class LogLevel(models.TextChoices):
    DEBUG = "debug", "Debug"
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"


class CalculationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        CalculationRun, on_delete=models.CASCADE, related_name="logs"
    )
    level = models.CharField(max_length=16, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
