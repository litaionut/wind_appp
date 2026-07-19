from django.urls import path

from apps.environment.api.views import NoiseRunView, ReceptorListCreateView, ShadowRunView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/environment/receptors/",
        ReceptorListCreateView.as_view(),
        name="environment-receptors",
    ),
    path(
        "projects/<uuid:project_id>/environment/noise-run/",
        NoiseRunView.as_view(),
        name="environment-noise-run",
    ),
    path(
        "projects/<uuid:project_id>/environment/shadow-run/",
        ShadowRunView.as_view(),
        name="environment-shadow-run",
    ),
]
