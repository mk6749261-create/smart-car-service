from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from maintenance.models import validate_is_technician


class ServiceSlot(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Available", "Available"
        BOOKED = "Booked", "Booked"
        BLOCKED = "Blocked", "Blocked"

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="slots",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_slots",
        limit_choices_to={"role": "Technician"},
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["service"]),
            models.Index(fields=["technician"]),
            models.Index(fields=["start_time"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["start_time"]

    def clean(self):
        validate_is_technician(self.technician_id)
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")

    def __str__(self):
        return f"{self.service} slot - {self.technician} @ {self.start_time:%Y-%m-%d %H:%M}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "Confirmed", "Confirmed"
        CANCELLED = "Cancelled", "Cancelled"
        COMPLETED = "Completed", "Completed"

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    slot = models.ForeignKey(
        ServiceSlot,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CONFIRMED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # A slot may have at most one *active* appointment at a time.
            # A Cancelled appointment no longer blocks that slot from
            # being booked again by someone else.
            models.UniqueConstraint(
                fields=["slot"],
                condition=models.Q(status__in=["Confirmed", "Completed"]),
                name="unique_active_appointment_per_slot",
            ),
        ]
        ordering = ["-created_at"]

    def clean(self):
        if self.slot_id and self.status in (self.Status.CONFIRMED, self.Status.COMPLETED):
            clashing = Appointment.objects.filter(
                slot_id=self.slot_id,
                status__in=[self.Status.CONFIRMED, self.Status.COMPLETED],
            ).exclude(pk=self.pk)
            if clashing.exists():
                raise ValidationError("This slot is already booked.")

    def __str__(self):
        return f"Appointment #{self.pk} - {self.vehicle} ({self.status})"
