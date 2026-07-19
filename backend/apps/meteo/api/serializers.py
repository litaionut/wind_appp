from rest_framework import serializers

from apps.meteo.models import MeasurementCampaign, Sensor


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ("id", "code", "variable", "height_m", "unit", "created_at")
        read_only_fields = ("id", "created_at")


class CampaignSerializer(serializers.ModelSerializer):
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = MeasurementCampaign
        fields = (
            "id",
            "project",
            "name",
            "structure_type",
            "latitude",
            "longitude",
            "elevation_m",
            "created_by",
            "created_at",
            "sensors",
        )
        read_only_fields = ("id", "project", "created_by", "created_at", "sensors")


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementCampaign
        fields = (
            "name",
            "structure_type",
            "latitude",
            "longitude",
            "elevation_m",
        )


class SensorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ("code", "variable", "height_m", "unit")
