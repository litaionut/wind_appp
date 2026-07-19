"""Project API URL routes."""

from django.urls import path

from apps.projects.api.member_views import (
    ProjectMemberDetailView,
    ProjectMemberListCreateView,
)
from apps.projects.api.views import OrganizationProjectListCreateView, ProjectDetailView

urlpatterns = [
    path(
        "organizations/<uuid:org_id>/projects/",
        OrganizationProjectListCreateView.as_view(),
        name="organization-projects",
    ),
    path(
        "projects/<uuid:project_id>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "projects/<uuid:project_id>/members/",
        ProjectMemberListCreateView.as_view(),
        name="project-members",
    ),
    path(
        "projects/<uuid:project_id>/members/<uuid:membership_id>/",
        ProjectMemberDetailView.as_view(),
        name="project-member-detail",
    ),
]
