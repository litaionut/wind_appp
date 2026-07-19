from django.urls import path

from apps.financial.api.views import ElectricalLossView, LCOENPVView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/financial/electrical-loss/",
        ElectricalLossView.as_view(),
        name="financial-electrical-loss",
    ),
    path(
        "projects/<uuid:project_id>/financial/lcoe-npv/",
        LCOENPVView.as_view(),
        name="financial-lcoe-npv",
    ),
]
