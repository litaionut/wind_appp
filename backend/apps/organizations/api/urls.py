"""Organization API URL routes."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.organizations.api.member_views import (
    OrganizationMemberDetailView,
    OrganizationMemberListCreateView,
)
from apps.organizations.api.views import OrganizationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")

urlpatterns = [
    path(
        "organizations/<uuid:org_id>/members/",
        OrganizationMemberListCreateView.as_view(),
        name="organization-members",
    ),
    path(
        "organizations/<uuid:org_id>/members/<uuid:membership_id>/",
        OrganizationMemberDetailView.as_view(),
        name="organization-member-detail",
    ),
    *router.urls,
]
