from django.contrib import admin

from apps.energy.models import (
    CtCurve,
    CtCurvePoint,
    EnergyAssessment,
    PowerCurve,
    PowerCurvePoint,
)


class PowerCurvePointInline(admin.TabularInline):
    model = PowerCurvePoint
    extra = 0


@admin.register(PowerCurve)
class PowerCurveAdmin(admin.ModelAdmin):
    list_display = ("name", "turbine_model", "air_density_ref_kg_m3")
    inlines = [PowerCurvePointInline]


class CtCurvePointInline(admin.TabularInline):
    model = CtCurvePoint
    extra = 0


@admin.register(CtCurve)
class CtCurveAdmin(admin.ModelAdmin):
    list_display = ("name", "turbine_model", "air_density_ref_kg_m3")
    inlines = [CtCurvePointInline]


@admin.register(EnergyAssessment)
class EnergyAssessmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "method_version", "created_at")
