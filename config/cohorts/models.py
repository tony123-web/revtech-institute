from django.contrib.auth.models import User
from django.db import models
import uuid, datetime
from courses.models import Program

class Cohort(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        Program,null=True, blank=True,
        on_delete=models.PROTECT,
        related_name="cohorts"
    )
    name = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        unique=True,null=True, blank=True,
    )
    description = models.TextField(
        blank=True
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    registration_deadline = models.DateField(blank=True, null=True)
    capacity = models.PositiveIntegerField(
        default=30
    )
    is_open = models.BooleanField(
        default=False
    )
    created= models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):

        return self.name


class SeminarRoom(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    cohort = models.OneToOneField(
        Cohort,
        on_delete=models.CASCADE,
        related_name="seminar_room"
    )
    title = models.CharField(
        max_length=200,
        default="Seminar Room"
    )
    description = models.TextField(
        blank=True
    )
    zoom_link = models.URLField(
        blank=True
    )
    whatsapp_link = models.URLField(
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.cohort.name} - Seminar Room"


class SeminarResource(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seminar_room = models.ForeignKey(
        SeminarRoom,
        on_delete=models.CASCADE,
        related_name="resources"
    )
    title = models.CharField(
        max_length=200
    )
    description = models.TextField(
        blank=True
    )
    url = models.URLField()
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class Discussion(models.Model):
    POST_TYPES = [
        ("question", "Question"),
        ("idea", "Idea"),
        ("announcement", "Announcement"),
    ]
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seminar_room = models.ForeignKey(
        SeminarRoom,
        on_delete=models.CASCADE,
        related_name="discussions"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cohort_discussions"
    )
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPES,
        default="question"
    )
    title = models.CharField(
        max_length=200
    )
    content = models.TextField()
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class DiscussionReply(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="discussion_replies"
    )
    content = models.TextField()
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.author.username}"



