from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "make", "model", "year", "license_plate", "owner")
    list_filter = ("make", "year")
    search_fields = ("make", "model", "license_plate", "owner__username")
