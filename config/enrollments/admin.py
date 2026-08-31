from django.contrib import admin

from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "cohort",
        "status",
        "payment_verified",
        "is_active",
        "amount_paid",
        "payment_date",
    )

    list_filter = (
        "status",
        "payment_verified",
        "is_active",
        "cohort",
    )

    search_fields = (
        "student__username",
        "student__email",
        "cohort__name",
        "payment_reference",
    )

    readonly_fields = (
        "payment_reference",
        "payment_date",
        "amount_paid",
    )