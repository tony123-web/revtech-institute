from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to="projects/",
        blank=True,
        null=True
    )
    technologies = models.CharField(max_length=500, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title