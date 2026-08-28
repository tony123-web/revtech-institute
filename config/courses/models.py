from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True
    )
    short_description = models.CharField(
        max_length=300
    )
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to="programs/",
        blank=True,
        null=True
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


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cohort = models.ForeignKey(
        "cohorts.Cohort",null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(
        max_length=200
    )
    description = models.TextField(
        blank=True
    )
    order = models.PositiveIntegerField(
        default=1
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )


    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["cohort", "order"],
                name="unique_module_order_per_program"
            )
        ]

    def __str__(self):
        return f"{self.cohort.name} - {self.title}"

class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(
        blank=True,
    )
    video_url = models.URLField(
        blank=True
    )
    duration_seconds = models.PositiveIntegerField(
        default=0
    )
    order = models.PositiveIntegerField(
        default=1
    )
    is_preview = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=True
    )
    created = models.DateTimeField(default=timezone.now,)
    updated = models.DateTimeField(default=timezone.now,)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module"
            ),

            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_lesson_slug_per_module"
            ),
        ]


    def __str__(self):

        return f"{self.module.title} - {self.title}"

class Assignment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    title = models.CharField(
        max_length=200
    )
    instructions = models.TextField()
    due_date = models.DateTimeField(
        blank=True,
        null=True
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
        return f"{self.lesson.title} - {self.title}"

class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_progress"
    )
    watched_seconds = models.PositiveIntegerField(
        default=0
    )
    completed = models.BooleanField(
        default=False
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson"],
                name="unique_student_lesson_progress"
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"









