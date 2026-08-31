from django.contrib.auth.models import User
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta


class Profile(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        INSTRUCTOR = "instructor", "Instructor"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    institution = models.CharField(
        max_length=200,
        blank=True
    )

    course = models.CharField(
        max_length=200,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    skills = models.TextField(
        blank=True,
        help_text="Separate skills with commas."
    )

    github_url = models.URLField(
        blank=True
    )

    linkedin_url = models.URLField(
        blank=True
    )

    portfolio_url = models.URLField(
        blank=True
    )

    central_url = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def is_complete(self):
        return all([
            self.user.first_name,
            self.user.last_name,
            self.profile_image,
            self.phone_number,
            self.institution,
            self.course,
            self.bio,
        ])

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="email_verification"
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def is_expired(self):
        return timezone.now() > (
                self.created_at + timedelta(hours=24)
        )

    def __str__(self):
        return f"Verification token for {self.user.email}"






