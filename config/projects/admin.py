from django.contrib import admin
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "student",
        "cohort",
        "is_featured",
        "is_published",
        "created_at",
    )

    list_filter = (
        "is_featured",
        "is_published",
        "cohort",
    )

    search_fields = (
        "title",
        "student__username",
        "student__first_name",
        "student__last_name",
    )

    inlines = [
        ProjectImageInline
    ]