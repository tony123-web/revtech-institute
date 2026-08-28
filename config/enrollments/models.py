from django.contrib.auth.models import User
from django.db import models
from cohorts.models import Cohort
import uuid


class Enrollment(models.Model):
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
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "cohort"],
                name="unique_student_cohort"
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.cohort.program.title}"