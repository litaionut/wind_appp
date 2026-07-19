from django.urls import path

from apps.operations.api.views import AvailabilityKPIView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/operations/availability-kpi/",
        AvailabilityKPIView.as_view(),
        name="operations-availability-kpi",
    ),
]
