"""Organization API URL routes."""

from rest_framework.routers import DefaultRouter

from apps.organizations.api.views import OrganizationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet, basename="organization")

urlpatterns = router.urls
