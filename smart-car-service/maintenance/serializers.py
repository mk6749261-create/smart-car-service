from rest_framework import serializers

from authentication.models import User
from vehicles.models import Vehicle

from .models import MaintenanceRecord, MaintenanceRequest


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    vehicle_license_plate = serializers.CharField(source="vehicle.license_plate", read_only=True)
    technician_username = serializers.CharField(source="technician.username", read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = (
            "id",
            "vehicle",
            "vehicle_license_plate",
            "service",
            "technician",
            "technician_username",
            "description",
            "priority",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "technician", "status", "created_at", "updated_at")

    def validate_vehicle(self, vehicle):
        """FR-09/NFR-04: a Customer may only file a request for their own vehicle."""
        request = self.context["request"]
        user = request.user
        if user.role == User.Role.CUSTOMER and vehicle.owner_id != user.id:
            raise serializers.ValidationError("You do not own this vehicle.")
        return vehicle


class AssignTechnicianSerializer(serializers.Serializer):
    """Used by the Manager-only assign_technician action."""

    technician = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.TECHNICIAN)
    )


class UpdateRequestStatusSerializer(serializers.Serializer):
    """Used by the assigned Technician (or Manager) to move the request forward."""

    status = serializers.ChoiceField(
        choices=[
            MaintenanceRequest.Status.IN_PROGRESS,
            MaintenanceRequest.Status.COMPLETED,
            MaintenanceRequest.Status.CANCELLED,
        ]
    )


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    vehicle_license_plate = serializers.CharField(source="vehicle.license_plate", read_only=True)
    technician_username = serializers.CharField(source="technician.username", read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = (
            "id",
            "vehicle",
            "vehicle_license_plate",
            "service",
            "technician",
            "technician_username",
            "maintenance_request",
            "description",
            "cost",
            "performed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_technician(self, technician):
        if technician.role != User.Role.TECHNICIAN:
            raise serializers.ValidationError("Assigned user must have the Technician role.")
        return technician
