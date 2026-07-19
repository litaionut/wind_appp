"""Core API views."""

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness endpoint — confirms the API process is responding.

    Does not probe the database (readiness split is deferred).
    Public by design (no authentication required).
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "ok",
                "service": "wind-platform-api",
                "api_version": "v1",
            }
        )
