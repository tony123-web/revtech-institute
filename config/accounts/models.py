from django.contrib.auth.models import User
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    profile_image = models.ImageField(
        upload_to="students/",
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    central_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username