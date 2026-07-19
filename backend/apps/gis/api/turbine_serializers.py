from rest_framework import serializers

from apps.gis.models import TurbineManufacturer, TurbineModel, TurbinePosition


class TurbineManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurbineManufacturer
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")


class TurbineModelSerializer(serializers.ModelSerializer):
    manufacturer_id = serializers.UUIDField(source="manufacturer.id", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    manufacturer_name_write = serializers.CharField(write_only=True, required=True)
    manufacturer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TurbineModel
        fields = (
            "id",
            "manufacturer",
            "manufacturer_id",
            "manufacturer_name",
            "manufacturer_name_write",
            "name",
            "hub_height_m",
            "rotor_diameter_m",
            "rated_power_kw",
            "created_at",
        )
        read_only_fields = (
            "id",
            "manufacturer",
            "manufacturer_id",
            "manufacturer_name",
            "created_at",
        )

    def validate(self, attrs: dict) -> dict:
        for field in ("hub_height_m", "rotor_diameter_m", "rated_power_kw"):
            if field in attrs and attrs[field] is not None and attrs[field] <= 0:
                raise serializers.ValidationError({field: "Must be greater than 0."})
        return attrs

    def create(self, validated_data: dict) -> TurbineModel:
        mfr_name = validated_data.pop("manufacturer_name_write")
        manufacturer, _ = TurbineManufacturer.objects.get_or_create(name=mfr_name.strip())
        validated_data["manufacturer"] = manufacturer
        return super().create(validated_data)


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
