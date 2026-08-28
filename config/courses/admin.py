from django.contrib import admin

from .models import (
    Program,
    Module,
    Lesson,
    LessonProgress,
    Assignment,
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
        "order",
        "is_active",
    )

    list_filter = (
        "cohort",
        "is_active",
    )

    search_fields = (
        "title",
        "cohort__title",
    )

    ordering = (
        "cohort",
        "order",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "module",
        "order",
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
        "due_date",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "title",
    )




