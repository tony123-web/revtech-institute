from django.contrib import admin

from .models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "lesson",
        "watched_seconds",
        "completed",
        "updated_at",
    )

    list_filter = ("completed",)

    search_fields = (
        "student__username",
        "lesson__title",
    )