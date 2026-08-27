from django.contrib import admin

from .models import Cohort


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_active",
        "is_published",
    )

    list_filter = (
        "is_active",
        "is_published",
    )