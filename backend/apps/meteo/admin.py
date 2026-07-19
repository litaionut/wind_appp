from django.contrib import admin

from apps.meteo.models import MeasurementCampaign, Sensor, TimeSeriesPoint


class SensorInline(admin.TabularInline):
    model = Sensor
    extra = 0


@admin.register(MeasurementCampaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "structure_type", "created_at")
    inlines = [SensorInline]


@admin.register(TimeSeriesPoint)
class TimeSeriesPointAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "sensor", "value", "qc_flag")
    list_filter = ("qc_flag",)
