"""Calculation API serializers."""

from rest_framework import serializers

from apps.calculations.models import CalculationLog, CalculationMethod, CalculationRun


class CalculationMethodSerializer(serializers.ModelSerializer):
    registry_key = serializers.CharField(read_only=True)

    class Meta:
        model = CalculationMethod
        fields = (
            "id",
            "method_id",
            "version",
            "registry_key",
            "title",
            "description",
            "status",
            "input_schema",
            "output_schema",
            "created_at",
        )
        read_only_fields = fields


class CalculationRunSerializer(serializers.ModelSerializer):
    method_key = serializers.CharField(source="method.registry_key", read_only=True)

    class Meta:
        model = CalculationRun
        fields = (
            "id",
            "organization",
            "project",
            "method",
            "method_key",
            "calculation_type",
            "application_version",
            "input_data_version",
            "parameters",
            "assumptions",
            "status",
            "started_at",
            "completed_at",
            "created_by",
            "results",
            "warnings",
            "errors",
            "validation_status",
            "created_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "project",
            "method_key",
            "status",
            "started_at",
            "completed_at",
            "created_by",
            "results",
            "warnings",
            "errors",
            "validation_status",
            "created_at",
        )


class CalculationRunCreateSerializer(serializers.Serializer):
    method_id = serializers.CharField()
    method_version = serializers.CharField()
    calculation_type = serializers.CharField(required=False, allow_blank=True)
    parameters = serializers.JSONField(required=False, default=dict)
    assumptions = serializers.JSONField(required=False, default=dict)
    input_data_version = serializers.CharField(required=False, allow_blank=True, default="")
    execute = serializers.BooleanField(required=False, default=True)


class CalculationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationLog
        fields = ("id", "level", "message", "created_at")
        read_only_fields = fields
