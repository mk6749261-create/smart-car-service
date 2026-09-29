from rest_framework import permissions, viewsets

from authentication.permissions import IsManager

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """FR-17: Service catalogue. Everyone authenticated can browse it,
    only a Manager can create/edit/delete a service."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManager()]
        return [permissions.IsAuthenticated()]
