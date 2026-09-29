from authentication.models import User
from config.exceptions import BusinessLogicError
from vehicles.models import Vehicle

from .models import MaintenanceRecord


def get_maintenance_history(user, vehicle_id):
    """
    FR-15/FR-16/FR-27/FR-36: maintenance history for a vehicle, respecting
    the same visibility rules as the REST API:
    - Customer: only their own vehicle
    - Technician / Manager: any vehicle (needed for operational work)
    """
    try:
        vehicle = Vehicle.objects.get(pk=vehicle_id)
    except Vehicle.DoesNotExist:
        raise BusinessLogicError(f"Vehicle {vehicle_id} was not found.")

    if user.role == User.Role.CUSTOMER and vehicle.owner_id != user.id:
        raise BusinessLogicError("You do not have access to this vehicle's maintenance history.")

    return (
        MaintenanceRecord.objects.filter(vehicle_id=vehicle_id)
        .select_related("service", "technician")
        .order_by("-performed_at")
    )
