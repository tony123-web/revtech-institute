from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in weeks"
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    content = models.TextField(blank=True)
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        default=0
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title










