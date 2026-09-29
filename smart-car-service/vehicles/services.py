from .models import Vehicle


def get_vehicles_for_customer(user):
    """FR-06/FR-26/FR-35: vehicles owned by the authenticated Customer."""
    return Vehicle.objects.filter(owner=user).order_by("-created_at")
