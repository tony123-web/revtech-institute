from django.contrib.auth.models import User
from django.db import models
import uuid

class Project(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    cohort = models.ForeignKey(
        "cohorts.Cohort",
        on_delete=models.CASCADE,
        related_name="projects"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    technologies = models.CharField(
        max_length=500,
        blank=True
    )

    github_url = models.URLField(
        blank=True
    )

    live_url = models.URLField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    is_published = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="projects/screenshots/"
    )

    caption = models.CharField(
        max_length=200,null=True,
        blank=True
    )

    order = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.project.title} - Screenshot"



