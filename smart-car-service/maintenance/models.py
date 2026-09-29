from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


def validate_is_technician(user_id):
    """Ensure the referenced user has the Technician role."""
    if user_id is None:
        return
    User = settings.AUTH_USER_MODEL
    from django.apps import apps

    user_model = apps.get_model(User)
    user = user_model.objects.filter(pk=user_id).first()
    if user and user.role != "Technician":
        raise ValidationError("Assigned user must have the Technician role.")


class MaintenanceRequest(models.Model):
    class Priority(models.TextChoices):
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"
        CRITICAL = "Critical", "Critical"

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ASSIGNED = "Assigned", "Assigned"
        IN_PROGRESS = "In Progress", "In Progress"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_requests",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_maintenance_requests",
        null=True,
        blank=True,
        limit_choices_to={"role": "Technician"},
    )
    description = models.TextField()
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle"]),
            models.Index(fields=["technician"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]

    def clean(self):
        if self.technician_id:
            validate_is_technician(self.technician_id)

    def __str__(self):
        return f"Request #{self.pk} - {self.vehicle} ({self.status})"


class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
        related_name="maintenance_records",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="performed_maintenance_records",
        limit_choices_to={"role": "Technician"},
    )
    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.SET_NULL,
        related_name="records",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    performed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle"]),
            models.Index(fields=["performed_at"]),
        ]
        ordering = ["-performed_at"]

    def clean(self):
        validate_is_technician(self.technician_id)

    def __str__(self):
        return f"Record #{self.pk} - {self.vehicle} ({self.performed_at:%Y-%m-%d})"
