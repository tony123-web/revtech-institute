from django.contrib.auth.models import User
from django.db import models
import uuid
from courses.models import Lesson


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