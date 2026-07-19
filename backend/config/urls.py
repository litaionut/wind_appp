"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.api.urls")),
    path("api/v1/auth/", include("apps.identity.api.urls")),
    path("api/v1/", include("apps.organizations.api.urls")),
    path("api/v1/", include("apps.projects.api.urls")),
]
