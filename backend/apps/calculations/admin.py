from django.contrib import admin

from apps.calculations.models import CalculationLog, CalculationMethod, CalculationRun


@admin.register(CalculationMethod)
class CalculationMethodAdmin(admin.ModelAdmin):
    list_display = ("method_id", "version", "status", "title")
    list_filter = ("status",)


class CalculationLogInline(admin.TabularInline):
    model = CalculationLog
    extra = 0
    readonly_fields = ("level", "message", "created_at")


@admin.register(CalculationRun)
class CalculationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "method", "status", "created_at")
    list_filter = ("status",)
    inlines = [CalculationLogInline]
