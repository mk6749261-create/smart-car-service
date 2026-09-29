from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.models import User
from authentication.permissions import IsCustomer, IsManagerOrTechnician
from config.exceptions import BusinessLogicError

from .models import Appointment, ServiceSlot
from .serializers import AppointmentSerializer, ServiceSlotSerializer
from .services import book_appointment_for_user


class ServiceSlotViewSet(viewsets.ModelViewSet):
    """FR-17/FR-18: technicians' bookable availability."""

    serializer_class = ServiceSlotSerializer

    def get_queryset(self):
        qs = ServiceSlot.objects.select_related("service", "technician")
        status_param = self.request.query_params.get("status")
        service_param = self.request.query_params.get("service")
        if status_param:
            qs = qs.filter(status=status_param)
        if service_param:
            qs = qs.filter(service_id=service_param)
        return qs

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsManagerOrTechnician()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == User.Role.TECHNICIAN:
            serializer.save(technician=user)
        else:
            serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    """FR-19..FR-23, including double-booking prevention (FR-21)."""

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related("vehicle", "slot", "slot__technician")
        if user.role == User.Role.CUSTOMER:
            return qs.filter(vehicle__owner=user)
        if user.role == User.Role.TECHNICIAN:
            return qs.filter(slot__technician=user)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCustomer()]
        if self.action == "cancel":
            return [permissions.IsAuthenticated()]
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsCustomer()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.validated_data["vehicle"]
        slot = serializer.validated_data["slot"]

        try:
            appointment = book_appointment_for_user(
                request.user, vehicle.id, slot.service_id, slot.id
            )
        except BusinessLogicError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        return Response(
            AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer):
        if serializer.instance.vehicle.owner_id != self.request.user.id:
            raise permissions.PermissionDenied("You do not own this appointment.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """FR-23: cancel an appointment and free up the slot again."""
        appointment = self.get_object()
        user = request.user
        is_owner = appointment.vehicle.owner_id == user.id
        if user.role == User.Role.CUSTOMER and not is_owner:
            return Response(
                {"detail": "You do not own this appointment."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if appointment.status == Appointment.Status.CANCELLED:
            return Response(
                {"detail": "Appointment is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            appointment.status = Appointment.Status.CANCELLED
            appointment.save(update_fields=["status", "updated_at"])
            slot = ServiceSlot.objects.select_for_update().get(pk=appointment.slot_id)
            slot.status = ServiceSlot.Status.AVAILABLE
            slot.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data)
