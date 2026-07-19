from django.contrib import admin

from apps.gis.models import (
    CoordinateReferenceSystem,
    ProjectBoundary,
    ProjectCRS,
    TurbineManufacturer,
    TurbineModel,
    TurbinePosition,
)


@admin.register(CoordinateReferenceSystem)
class CRSAdmin(admin.ModelAdmin):
    list_display = ("epsg_code", "name", "auth_name")
    search_fields = ("epsg_code", "name")


@admin.register(ProjectCRS)
class ProjectCRSAdmin(admin.ModelAdmin):
    list_display = ("project", "role", "crs")


@admin.register(TurbineManufacturer)
class TurbineManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(TurbineModel)
class TurbineModelAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "rated_power_kw", "rotor_diameter_m")
    list_filter = ("manufacturer",)


@admin.register(TurbinePosition)
class TurbinePositionAdmin(admin.ModelAdmin):
    list_display = ("label", "project", "x", "y", "turbine_model")
    list_filter = ("project",)


@admin.register(ProjectBoundary)
class ProjectBoundaryAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "kind", "created_at")
    list_filter = ("kind",)
