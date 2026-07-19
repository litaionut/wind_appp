"""Calculation API URL routes."""

from django.urls import path

from apps.calculations.api.views import (
    CalculationMethodListView,
    CalculationRunDetailView,
    CalculationRunLogListView,
    ProjectCalculationRunListCreateView,
)

urlpatterns = [
    path(
        "calculation-methods/",
        CalculationMethodListView.as_view(),
        name="calculation-methods",
    ),
    path(
        "projects/<uuid:project_id>/calculation-runs/",
        ProjectCalculationRunListCreateView.as_view(),
        name="project-calculation-runs",
    ),
    path(
        "calculation-runs/<uuid:run_id>/",
        CalculationRunDetailView.as_view(),
        name="calculation-run-detail",
    ),
    path(
        "calculation-runs/<uuid:run_id>/logs/",
        CalculationRunLogListView.as_view(),
        name="calculation-run-logs",
    ),
]
