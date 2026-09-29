from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Object-level check (NFR-04): a Customer may only modify a vehicle
    they own. Read access for non-owners (e.g. Manager/Technician) is
    handled separately via queryset filtering in the view, not here.
    """

    message = "You do not own this vehicle."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
