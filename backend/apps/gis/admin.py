from django.contrib import admin

from apps.gis.models import CoordinateReferenceSystem, ProjectCRS


@admin.register(CoordinateReferenceSystem)
class CRSAdmin(admin.ModelAdmin):
    list_display = ("epsg_code", "name", "auth_name")
    search_fields = ("epsg_code", "name")


@admin.register(ProjectCRS)
class ProjectCRSAdmin(admin.ModelAdmin):
    list_display = ("project", "role", "crs")
