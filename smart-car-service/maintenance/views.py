from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.models import User
from authentication.permissions import IsCustomer, IsManager, IsManagerOrTechnician

from .models import MaintenanceRecord, MaintenanceRequest
from .permissions import IsRequestParticipantOrManager
from .serializers import (
    AssignTechnicianSerializer,
    MaintenanceRecordSerializer,
    MaintenanceRequestSerializer,
    UpdateRequestStatusSerializer,
)


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """FR-10..FR-14."""

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = MaintenanceRequest.objects.select_related("vehicle", "technician")
        if user.role == User.Role.CUSTOMER:
            return qs.filter(vehicle__owner=user)
        if user.role == User.Role.TECHNICIAN:
            return qs.filter(technician=user)
        return qs  # Manager sees everything

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCustomer()]
        if self.action in ("retrieve", "list"):
            return [permissions.IsAuthenticated(), IsRequestParticipantOrManager()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManager()]
        if self.action == "assign_technician":
            return [permissions.IsAuthenticated(), IsManager()]
        if self.action == "update_status":
            return [permissions.IsAuthenticated(), IsManagerOrTechnician()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def assign_technician(self, request, pk=None):
        """FR-13: Manager assigns a Technician to a request."""
        maintenance_request = self.get_object()
        serializer = AssignTechnicianSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maintenance_request.technician = serializer.validated_data["technician"]
        maintenance_request.status = MaintenanceRequest.Status.ASSIGNED
        maintenance_request.full_clean()
        maintenance_request.save()
        return Response(MaintenanceRequestSerializer(maintenance_request).data)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """FR-14: the assigned Technician (or a Manager) updates progress."""
        maintenance_request = self.get_object()
        user = request.user
        if user.role == User.Role.TECHNICIAN and maintenance_request.technician_id != user.id:
            return Response(
                {"detail": "You are not assigned to this request."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UpdateRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        maintenance_request.status = serializer.validated_data["status"]
        maintenance_request.save(update_fields=["status", "updated_at"])
        return Response(MaintenanceRequestSerializer(maintenance_request).data)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """FR-15/FR-16: maintenance history."""

    serializer_class = MaintenanceRecordSerializer

    def get_queryset(self):
        user = self.request.user
        qs = MaintenanceRecord.objects.select_related("vehicle", "technician")
        if user.role == User.Role.CUSTOMER:
            return qs.filter(vehicle__owner=user)
        if user.role == User.Role.TECHNICIAN:
            return qs.filter(technician=user)
        return qs

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManagerOrTechnician()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.TECHNICIAN:
            serializer.save(technician=user, performed_at=serializer.validated_data.get("performed_at") or timezone.now())
        else:
            serializer.save()
