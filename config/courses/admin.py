from django.contrib import admin

from .models import (
    Program,
    Module,
    Lesson,
    LessonProgress,
    Assignment,
    AssignmentSubmission
)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "cohort",
        "week",
        "order",
        "is_active",
    )

    list_filter = (
        "cohort",
        "week",
        "is_active",
    )

    search_fields = (
        "title",
        "cohort__title",
        "week__title"
    )

    ordering = (
        "cohort",
        "week__week_number",
        "order",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "module",
        "order",
        "video_file",
        "is_preview",
        "is_active",
    )

    list_filter = (
        "is_preview",
        "is_active",
    )

    search_fields = (
        "title",
        "module__title",
        "module__program__title",
    )

    ordering = (
        "module",
        "order",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "lesson",
        "watched_seconds",
        "completed",
        "updated_at",
    )

    list_filter = (
        "completed",
    )

    search_fields = (
        "student__username",
        "lesson__title",
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "due_date",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "due_date",
    )

    search_fields = (
        "title",
        "instructions",
        "lesson__title",
    )

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        "assignment",
        "student",
        "submitted_at",
        "is_visible_to_cohort",
    )

    list_filter = (
        "is_visible_to_cohort",
        "submitted_at",
    )

    search_fields = (
        "student__username",
        "assignment__title",
        "github_url",
        "comment",
    )




