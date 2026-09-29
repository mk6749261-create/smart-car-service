from django.contrib import admin

from .models import Appointment, ServiceSlot


@admin.register(ServiceSlot)
class ServiceSlotAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "technician", "start_time", "end_time", "status")
    list_filter = ("status", "service")
    search_fields = ("technician__username",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "slot", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("vehicle__license_plate",)
