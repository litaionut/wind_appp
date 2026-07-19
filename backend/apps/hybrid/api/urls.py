from django.urls import path

from apps.hybrid.api.views import HybridCurtailmentView, PVYieldView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/hybrid/pv-yield/",
        PVYieldView.as_view(),
        name="hybrid-pv-yield",
    ),
    path(
        "projects/<uuid:project_id>/hybrid/curtailment/",
        HybridCurtailmentView.as_view(),
        name="hybrid-curtailment",
    ),
]
