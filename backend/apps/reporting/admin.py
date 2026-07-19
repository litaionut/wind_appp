from django.contrib import admin

from apps.reporting.models import ReportArtifact


@admin.register(ReportArtifact)
class ReportArtifactAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "calculation_run", "created_at")
