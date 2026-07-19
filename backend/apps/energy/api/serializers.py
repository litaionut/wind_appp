from rest_framework import serializers

from apps.energy.models import (
    CtCurve,
    CtCurvePoint,
    EnergyAssessment,
    PowerCurve,
    PowerCurvePoint,
)


class PowerCurvePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerCurvePoint
        fields = ("wind_speed_m_s", "power_kw")


class PowerCurveSerializer(serializers.ModelSerializer):
    points = PowerCurvePointSerializer(many=True, read_only=True)

    class Meta:
        model = PowerCurve
        fields = (
            "id",
            "turbine_model",
            "name",
            "air_density_ref_kg_m3",
            "points",
            "created_at",
        )
        read_only_fields = ("id", "points", "created_at")


class CtCurvePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CtCurvePoint
        fields = ("wind_speed_m_s", "ct")


class CtCurveSerializer(serializers.ModelSerializer):
    points = CtCurvePointSerializer(many=True, read_only=True)

    class Meta:
        model = CtCurve
        fields = (
            "id",
            "turbine_model",
            "name",
            "air_density_ref_kg_m3",
            "points",
            "created_at",
        )
        read_only_fields = ("id", "points", "created_at")


class EnergyAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyAssessment
        fields = (
            "id",
            "project",
            "name",
            "power_curve",
            "wind_distribution",
            "wake_loss_fraction",
            "method_version",
            "results",
            "created_by",
            "created_at",
        )
        read_only_fields = (
            "id",
            "project",
            "method_version",
            "results",
            "created_by",
            "created_at",
        )
