from django.contrib.auth.models import User
from django.db import models
from courses.models import Course
from cohorts.models import Cohort


class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    cohort = models.ForeignKey(
        Cohort,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "cohort"],
                name="unique_student_course_cohort"
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"