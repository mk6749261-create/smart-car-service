from django.db import transaction

from authentication.models import User
from config.exceptions import BusinessLogicError
from services.models import Service
from vehicles.models import Vehicle

from .models import Appointment, ServiceSlot


def get_available_slots(service_id):
    """FR-18/FR-28/FR-37: available appointment slots for a given service."""
    if not Service.objects.filter(pk=service_id).exists():
        raise BusinessLogicError(f"Service {service_id} was not found.")

    return (
        ServiceSlot.objects.filter(service_id=service_id, status=ServiceSlot.Status.AVAILABLE)
        .select_related("technician")
        .order_by("start_time")
    )


def book_appointment_for_user(user, vehicle_id, service_id, slot_id):
    """
    FR-19/FR-20/FR-21/FR-38: the single source of truth for booking an
    appointment. Used by both the REST API (AppointmentViewSet) and the AI
    Agent's book_appointment tool, so the business rules can never diverge
    between the two entry points (FR-32/FR-42).
    """
    if user.role != User.Role.CUSTOMER:
        raise BusinessLogicError("Only a Customer account can book an appointment.")

    try:
        vehicle = Vehicle.objects.get(pk=vehicle_id)
    except Vehicle.DoesNotExist:
        raise BusinessLogicError(f"Vehicle {vehicle_id} was not found.")
    if vehicle.owner_id != user.id:
        raise BusinessLogicError("You do not own this vehicle.")

    try:
        slot = ServiceSlot.objects.get(pk=slot_id)
    except ServiceSlot.DoesNotExist:
        raise BusinessLogicError(f"Slot {slot_id} was not found.")
    if slot.service_id != int(service_id):
        raise BusinessLogicError("This slot does not belong to the requested service.")

    # FR-21: lock the row for the duration of the transaction so two
    # concurrent bookings can never both succeed on the same slot.
    with transaction.atomic():
        locked_slot = ServiceSlot.objects.select_for_update().get(pk=slot.pk)
        if locked_slot.status != ServiceSlot.Status.AVAILABLE:
            raise BusinessLogicError("This slot is no longer available.")
        appointment = Appointment.objects.create(vehicle=vehicle, slot=locked_slot)
        locked_slot.status = ServiceSlot.Status.BOOKED
        locked_slot.save(update_fields=["status"])

    return appointment
