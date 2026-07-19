from rest_framework import serializers

from apps.gis.models import CoordinateReferenceSystem, ProjectCRS


class CRSSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoordinateReferenceSystem
        fields = ("id", "epsg_code", "name", "auth_name", "created_at")
        read_only_fields = ("id", "created_at")


class ProjectCRSSerializer(serializers.ModelSerializer):
    epsg_code = serializers.IntegerField(source="crs.epsg_code", read_only=True)
    crs_name = serializers.CharField(source="crs.name", read_only=True)

    class Meta:
        model = ProjectCRS
        fields = ("id", "project", "crs", "epsg_code", "crs_name", "role", "created_at")
        read_only_fields = ("id", "project", "epsg_code", "crs_name", "created_at")


class ProjectCRSAssignSerializer(serializers.Serializer):
    epsg_code = serializers.IntegerField(min_value=1)
    name = serializers.CharField(required=False, allow_blank=True, default="")
    role = serializers.ChoiceField(choices=["horizontal", "display"], default="horizontal")


class TransformSerializer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    source_epsg = serializers.IntegerField(min_value=1)
    target_epsg = serializers.IntegerField(min_value=1)
