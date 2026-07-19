from django.urls import path

from apps.suitability.api.views import IECClassView, TerrainComplexityView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/suitability/iec-class/",
        IECClassView.as_view(),
        name="suitability-iec-class",
    ),
    path(
        "projects/<uuid:project_id>/suitability/terrain/",
        TerrainComplexityView.as_view(),
        name="suitability-terrain",
    ),
]
