from rest_framework import permissions, viewsets

from authentication.models import User
from authentication.permissions import IsCustomer

from .models import Vehicle
from .permissions import IsOwner
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    """
    FR-05..FR-09: Customers manage their own vehicles.
    Managers/Technicians get read-only access to all vehicles (they need
    this to work maintenance requests/appointments against a vehicle).
    """

    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.CUSTOMER:
            return Vehicle.objects.filter(owner=user)
        return Vehicle.objects.all()

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.IsAuthenticated, IsCustomer]
        elif self.action in ("update", "partial_update", "destroy"):
            permission_classes = [permissions.IsAuthenticated, IsCustomer, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
