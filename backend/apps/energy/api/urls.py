from django.urls import path

from apps.energy.api.views import (
    PowerCurveImportView,
    PowerCurveListCreateView,
    ProjectEnergyAssessmentListCreateView,
)

urlpatterns = [
    path("energy/power-curves/", PowerCurveListCreateView.as_view(), name="power-curves"),
    path(
        "energy/power-curves/<uuid:curve_id>/import/",
        PowerCurveImportView.as_view(),
        name="power-curve-import",
    ),
    path(
        "projects/<uuid:project_id>/energy-assessments/",
        ProjectEnergyAssessmentListCreateView.as_view(),
        name="project-energy-assessments",
    ),
]
