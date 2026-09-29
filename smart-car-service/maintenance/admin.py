from django.contrib import admin

from .models import MaintenanceRecord, MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "service", "technician", "priority", "status", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("vehicle__license_plate", "description")


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "service", "technician", "cost", "performed_at")
    list_filter = ("service",)
    search_fields = ("vehicle__license_plate",)
