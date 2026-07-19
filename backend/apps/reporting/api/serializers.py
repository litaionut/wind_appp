from rest_framework import serializers

from apps.reporting.models import ReportArtifact


class ReportArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportArtifact
        fields = (
            "id",
            "organization",
            "project",
            "calculation_run",
            "name",
            "content_type",
            "file",
            "summary",
            "created_by",
            "created_at",
        )
        read_only_fields = fields


class ReportGenerateSerializer(serializers.Serializer):
    calculation_run_id = serializers.UUIDField(required=False, allow_null=True)
