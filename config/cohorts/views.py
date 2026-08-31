from django.shortcuts import get_object_or_404, render
from .models import Cohort
from enrollments.models import Enrollment


def cohort_list(request):
    cohorts = Cohort.objects.filter(
        is_open=True
    ).select_related(
        "program"
    )

    return render(
        request,
        "cohorts/cohort_list.html",
        {
            "cohorts": cohorts
        }
    )


def cohort_detail(request, slug):
    cohort = get_object_or_404(
        Cohort.objects.select_related("program"),
        slug=slug
    )

    return render(
        request,
        "cohorts/cohort_detail.html",
        {
            "cohort": cohort
        }
    )




def upcoming_cohort(request):
    cohort = (
        Cohort.objects
        .filter(is_open=True)
        .select_related("program")
        .prefetch_related(
            "weeks__modules__lessons"
        )
        .order_by("start_date")
        .first()
    )
    available_spots = None

    if cohort:
        active_enrollments = Enrollment.objects.filter(
            cohort=cohort,
            status=Enrollment.Status.ACTIVE
        ).count()

        available_spots = max(
            cohort.capacity - active_enrollments,
            0
        )
    return render(
        request,
        "cohorts/upcoming_cohort.html",
        {
            "cohort": cohort,
            "available_spots":available_spots,
        }
    )








