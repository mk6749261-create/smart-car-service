from rest_framework import serializers

from authentication.models import User

from .models import Appointment, ServiceSlot


class ServiceSlotSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    technician_username = serializers.CharField(source="technician.username", read_only=True)

    class Meta:
        model = ServiceSlot
        fields = (
            "id",
            "service",
            "service_name",
            "technician",
            "technician_username",
            "start_time",
            "end_time",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")
        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    vehicle_license_plate = serializers.CharField(source="vehicle.license_plate", read_only=True)
    slot_detail = ServiceSlotSerializer(source="slot", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "vehicle",
            "vehicle_license_plate",
            "slot",
            "slot_detail",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate_vehicle(self, vehicle):
        """FR-20: vehicle ownership check."""
        request = self.context["request"]
        user = request.user
        if user.role == User.Role.CUSTOMER and vehicle.owner_id != user.id:
            raise serializers.ValidationError("You do not own this vehicle.")
        return vehicle

    def validate_slot(self, slot):
        """FR-20/FR-21: slot must exist and be available (final race-safe
        check happens again inside the view's atomic transaction)."""
        if slot.status != ServiceSlot.Status.AVAILABLE:
            raise serializers.ValidationError("This slot is no longer available.")
        return slot
