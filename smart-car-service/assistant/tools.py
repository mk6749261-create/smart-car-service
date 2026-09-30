"""
Agent tool implementations (FR-35..FR-38).

Every function here:
  - takes (user, params) and returns plain, JSON-serialisable data
  - re-validates identity/permissions itself (FR-33), never trusting that
    the Agent "should" only call it correctly
  - calls into each app's services.py (predefined Django business logic,
    FR-32/FR-42) - it never touches the database directly
  - raises ToolError with a short, user-safe message on any failure
    (FR-29/FR-41), which the agent then reports back to the model as a
    normal tool_result so the assistant can explain it to the user
"""

from authentication.models import User
from appointments.services import book_appointment_for_user, get_available_slots
from config.exceptions import BusinessLogicError
from maintenance.services import get_maintenance_history
from vehicles.services import get_vehicles_for_customer


# class ToolError(Exception):
#     pass


# def _require_int(params, name):
#     value = params.get(name)
#     if value is None:
#         raise ToolError(f"'{name}' is required.")
#     try:
#         return int(value)
#     except (TypeError, ValueError):
#         raise ToolError(f"'{name}' must be a number.")


# def tool_get_user_vehicles(user, params):
#     """FR-35/FR-26: vehicles owned by the authenticated Customer."""
#     if user.role != User.Role.CUSTOMER:
#         raise ToolError("Only a Customer account has vehicles to list this way.")
#     vehicles = get_vehicles_for_customer(user)
#     return [
#         {
#             "id": v.id,
#             "make": v.make,
#             "model": v.model,
#             "year": v.year,
#             "license_plate": v.license_plate,
#         }
#         for v in vehicles
#     ]


# def tool_get_maintenance_history(user, params):
#     """FR-36/FR-27: maintenance history for a vehicle the user can access."""
#     vehicle_id = _require_int(params, "vehicle_id")
#     try:
#         records = get_maintenance_history(user, vehicle_id)
#     except BusinessLogicError as exc:
#         raise ToolError(str(exc))
#     return [
#         {
#             "id": r.id,
#             "service": r.service.name,
#             "description": r.description,
#             "cost": str(r.cost) if r.cost is not None else None,
#             "performed_at": r.performed_at.isoformat(),
#         }
#         for r in records
#     ]


# def tool_get_available_slots(user, params):
#     """FR-37/FR-28: available slots for a requested service."""
#     service_id = _require_int(params, "service_id")
#     try:
#         slots = get_available_slots(service_id)
#     except BusinessLogicError as exc:
#         raise ToolError(str(exc))
#     return [
#         {
#             "id": s.id,
#             "technician": s.technician.username,
#             "start_time": s.start_time.isoformat(),
#             "end_time": s.end_time.isoformat(),
#         }
#         for s in slots
#     ]


# def tool_book_appointment(user, params):
#     """FR-38/FR-19..FR-21: book an appointment (critical action - the agent
#     layer requires explicit user confirmation before this ever runs, see
#     assistant/agent.py CONFIRMATION_REQUIRED_TOOLS)."""
#     vehicle_id = _require_int(params, "vehicle_id")
#     service_id = _require_int(params, "service_id")
#     slot_id = _require_int(params, "slot_id")
#     try:
#         appointment = book_appointment_for_user(user, vehicle_id, service_id, slot_id)
#     except BusinessLogicError as exc:
#         raise ToolError(str(exc))
#     return {
#         "appointment_id": appointment.id,
#         "status": appointment.status,
#         "slot_id": appointment.slot_id,
#     }


# TOOLS = {
#     "get_user_vehicles": tool_get_user_vehicles,
#     "get_maintenance_history": tool_get_maintenance_history,
#     "get_available_slots": tool_get_available_slots,
#     "book_appointment": tool_book_appointment,
# }


from authentication.models import User
from appointments.services import book_appointment_for_user, get_available_slots
from config.exceptions import BusinessLogicError
from maintenance.services import get_maintenance_history
from vehicles.services import get_vehicles_for_customer


class ToolError(Exception):
    pass


def _require_int(params, name):
    value = params.get(name)
    if value is None:
        raise ToolError(f"'{name}' is required.")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ToolError(f"'{name}' must be a number.")


def tool_get_user_vehicles(user, params):
    """FR-35/FR-26: vehicles owned by the authenticated Customer."""
    if user.role != User.Role.CUSTOMER:
        raise ToolError("Only a Customer account has vehicles to list this way.")
    vehicles = get_vehicles_for_customer(user)
    return [
        {
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "license_plate": v.license_plate,
        }
        for v in vehicles
    ]


def tool_get_maintenance_history(user, params):
    """FR-36/FR-27: maintenance history for a vehicle the user can access."""
    vehicle_id = _require_int(params, "vehicle_id")
    try:
        records = get_maintenance_history(user, vehicle_id)
    except BusinessLogicError as exc:
        raise ToolError(str(exc))
    return [
        {
            "id": r.id,
            "service": r.service.name,
            "description": r.description,
            "cost": str(r.cost) if r.cost is not None else None,
            "performed_at": r.performed_at.isoformat(),
        }
        for r in records
    ]


def tool_get_available_slots(user, params):
    """FR-37/FR-28: available slots for a requested service."""
    service_id = _require_int(params, "service_id")
    try:
        slots = get_available_slots(service_id)
    except BusinessLogicError as exc:
        raise ToolError(str(exc))
    return [
        {
            "id": s.id,
            "technician": s.technician.username,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
        }
        for s in slots
    ]


def tool_book_appointment(user, params):
    """FR-38/FR-19..FR-21: book an appointment (critical action - the agent
    layer requires explicit user confirmation before this ever runs, see
    assistant/agent.py CONFIRMATION_REQUIRED_TOOLS)."""
    vehicle_id = _require_int(params, "vehicle_id")
    service_id = _require_int(params, "service_id")
    slot_id = _require_int(params, "slot_id")
    try:
        appointment = book_appointment_for_user(user, vehicle_id, service_id, slot_id)
    except BusinessLogicError as exc:
        raise ToolError(str(exc))
    return {
        "appointment_id": appointment.id,
        "status": appointment.status,
        "slot_id": appointment.slot_id,
    }


TOOLS = {
    "get_user_vehicles": tool_get_user_vehicles,
    "get_maintenance_history": tool_get_maintenance_history,
    "get_available_slots": tool_get_available_slots,
    "book_appointment": tool_book_appointment,
}
