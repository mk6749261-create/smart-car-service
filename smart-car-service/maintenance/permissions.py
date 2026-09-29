from rest_framework.permissions import SAFE_METHODS, BasePermission

from authentication.models import User


class IsRequestParticipantOrManager(BasePermission):
    """
    Object-level check for a MaintenanceRequest:
    - Manager: full access
    - Customer: read-only, and only for their own vehicle
    - Technician: read-only, and only if assigned to this request
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Role.MANAGER:
            return True
        if request.method not in SAFE_METHODS:
            return False
        if user.role == User.Role.CUSTOMER:
            return obj.vehicle.owner_id == user.id
        if user.role == User.Role.TECHNICIAN:
            return obj.technician_id == user.id
        return False
