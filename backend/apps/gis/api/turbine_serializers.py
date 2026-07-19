from rest_framework import serializers

from apps.gis.models import TurbineManufacturer, TurbineModel, TurbinePosition


class TurbineManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurbineManufacturer
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")


class TurbineModelSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)

    class Meta:
        model = TurbineModel
        fields = (
            "id",
            "manufacturer",
            "manufacturer_name",
            "name",
            "hub_height_m",
            "rotor_diameter_m",
            "rated_power_kw",
            "created_at",
        )
        read_only_fields = ("id", "manufacturer_name", "created_at")


class TurbinePositionSerializer(serializers.ModelSerializer):
    turbine_model_name = serializers.CharField(
        source="turbine_model.name", read_only=True, default=None
    )
    epsg_code = serializers.IntegerField(source="crs.epsg_code", read_only=True, default=None)

    class Meta:
        model = TurbinePosition
        fields = (
            "id",
            "project",
            "turbine_model",
            "turbine_model_name",
            "label",
            "x",
            "y",
            "z",
            "crs",
            "epsg_code",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "project",
            "turbine_model_name",
            "epsg_code",
            "created_by",
            "created_at",
            "updated_at",
        )


class TurbinePositionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurbinePosition
        fields = ("turbine_model", "label", "x", "y", "z")
