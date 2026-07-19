"""Audit API URL routes."""

from django.urls import path

from apps.audit.api.views import OrganizationAuditEventListView, ProjectAuditEventListView

urlpatterns = [
    path(
        "organizations/<uuid:org_id>/audit-events/",
        OrganizationAuditEventListView.as_view(),
        name="organization-audit-events",
    ),
    path(
        "projects/<uuid:project_id>/audit-events/",
        ProjectAuditEventListView.as_view(),
        name="project-audit-events",
    ),
]
