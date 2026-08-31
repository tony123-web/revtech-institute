from django.contrib.auth.models import User
from django.db import models
from cohorts.models import Cohort
import uuid


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True
    )

    payment_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=False
    )

    payment_reference = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.cohort.name}"