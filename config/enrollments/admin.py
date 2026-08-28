from django.contrib import admin

from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "cohort",
        "payment_verified",
        "is_active",
        "enrolled_at",
    )

    list_filter = (
        "payment_verified",
        "is_active",
        "cohort",
    )

    search_fields = (
        "student__username",
        "student__email",
        "cohort__name",
    )

    ordering = (
        "-enrolled_at",
    )