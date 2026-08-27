from django.contrib.auth.models import User
from django.db import models


class Cohort(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    students = models.ManyToManyField(
        User,
        related_name="cohorts",
        blank=True
    )

    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name