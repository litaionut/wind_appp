"""CSV export for turbine layouts."""

import csv
import io

from django.http import HttpResponse
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.gis.models import TurbinePosition
from apps.projects.models import Project


class ProjectTurbinesCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_id) -> HttpResponse:
        if request.user.is_superuser:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist as exc:
                raise NotFound() from exc
        else:
            try:
                project = (
                    Project.objects.filter(memberships__user=request.user)
                    .distinct()
                    .get(id=project_id)
                )
            except Project.DoesNotExist as exc:
                raise NotFound() from exc

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["label", "x", "y", "z", "model"])
        for t in TurbinePosition.objects.filter(project=project).select_related(
            "turbine_model"
        ):
            writer.writerow(
                [
                    t.label,
                    t.x,
                    t.y,
                    "" if t.z is None else t.z,
                    t.turbine_model.name if t.turbine_model_id else "",
                ]
            )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{project.slug}_turbines.csv"'
        )
        return response
