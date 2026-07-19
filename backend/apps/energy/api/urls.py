from django.urls import path

from apps.energy.api.advanced_views import JensenWakeView, MCPLinearView, UncertaintyView
from apps.energy.api.views import (
    CtCurveImportView,
    CtCurveListCreateView,
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
    path("energy/ct-curves/", CtCurveListCreateView.as_view(), name="ct-curves"),
    path(
        "energy/ct-curves/<uuid:curve_id>/import/",
        CtCurveImportView.as_view(),
        name="ct-curve-import",
    ),
    path(
        "projects/<uuid:project_id>/energy-assessments/",
        ProjectEnergyAssessmentListCreateView.as_view(),
        name="project-energy-assessments",
    ),
    path(
        "projects/<uuid:project_id>/energy/mcp-linear/",
        MCPLinearView.as_view(),
        name="energy-mcp-linear",
    ),
    path(
        "projects/<uuid:project_id>/energy/wake-jensen/",
        JensenWakeView.as_view(),
        name="energy-wake-jensen",
    ),
    path(
        "projects/<uuid:project_id>/energy-assessments/<uuid:assessment_id>/uncertainty/",
        UncertaintyView.as_view(),
        name="energy-uncertainty",
    ),
]
