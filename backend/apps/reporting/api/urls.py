from django.urls import path

from apps.reporting.api.views import ProjectReportListCreateView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/reports/",
        ProjectReportListCreateView.as_view(),
        name="project-reports",
    ),
]
